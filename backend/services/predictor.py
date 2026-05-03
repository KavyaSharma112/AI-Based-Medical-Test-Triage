"""
Prediction Service (v2 — Clinically Calibrated)
=================================================
Changes from v1:
  - Raw model probability is ADJUSTED using clinical sanity check
  - Each prediction includes raw_model_probability, adjusted probability,
    clinical_risk_score, confidence_note, and abnormal_markers list
  - Risk level is determined from ADJUSTED probability, not raw model output
  - Confidence note explains WHY the risk was adjusted
"""

import numpy as np
from schemas.input_schema import MasterInputSchema, PredictionResult
from services.feature_mapper import (
    map_kidney_features, get_kidney_features_used,
    map_heart_features, get_heart_features_used,
    map_liver_features, get_liver_features_used,
    map_diabetes_features, get_diabetes_features_used,
)
from services.clinical_checker import (
    compute_clinical_score, apply_clinical_adjustment, get_confidence_note,
    KIDNEY_KEY_MARKERS, HEART_KEY_MARKERS, LIVER_KEY_MARKERS, DIABETES_KEY_MARKERS,
)


def probability_to_risk(prob: float) -> str:
    if prob < 0.35:
        return "Low"
    elif prob < 0.60:
        return "Moderate"
    else:
        return "High"


RECOMMENDATIONS = {
    "Kidney Disease": {
        "Low":      "Your kidney indicators appear within normal range. Stay hydrated and maintain annual check-ups.",
        "Moderate": "Some kidney indicators are concerning. Reduce salt intake, stay hydrated, and consult a nephrologist.",
        "High":     "Multiple kidney risk factors detected. Please consult a nephrologist promptly for further evaluation.",
    },
    "Heart Disease": {
        "Low":      "Your cardiac indicators appear within normal range. Maintain a heart-healthy diet and regular exercise.",
        "Moderate": "Some cardiac risk factors are present. Consider lifestyle changes and consult a cardiologist.",
        "High":     "Significant cardiac risk factors detected. Please consult a cardiologist promptly for evaluation.",
    },
    "Liver Disease": {
        "Low":      "Your liver function indicators appear within normal range. Limit alcohol and maintain a healthy diet.",
        "Moderate": "Some liver function markers are elevated. Avoid alcohol, reduce fatty foods, and consult a hepatologist.",
        "High":     "Multiple liver function abnormalities detected. Please consult a hepatologist promptly.",
    },
    "Diabetes": {
        "Low":      "Your metabolic indicators suggest low diabetes risk. Maintain a balanced diet and regular exercise.",
        "Moderate": "Some metabolic risk factors are present. Monitor blood sugar, reduce sugary foods, and consult a doctor.",
        "High":     "Significant diabetes risk factors detected. Please consult an endocrinologist for glucose testing.",
    },
}


def get_recommendation(disease: str, risk: str) -> str:
    return RECOMMENDATIONS.get(disease, {}).get(risk, "Please consult a healthcare professional.")


def _run_prediction(disease_name, model_bundle, feature_array, clinical_score, features_used):
    model = model_bundle["model"]
    scaler = model_bundle.get("scaler")

    X = feature_array.copy()
    if scaler is not None:
        X = scaler.transform(X)

    raw_prob = float(model.predict_proba(X)[0][1])
    adjusted_prob = apply_clinical_adjustment(raw_prob, clinical_score)
    risk = probability_to_risk(adjusted_prob)
    confidence_note = get_confidence_note(clinical_score, raw_prob, adjusted_prob)

    return PredictionResult(
        disease=disease_name,
        risk_level=risk,
        probability=round(adjusted_prob, 4),
        percentage=int(adjusted_prob * 100),
        recommendation=get_recommendation(disease_name, risk),
        features_used=features_used,
        model_available=True,
        raw_model_probability=round(raw_prob, 4),
        clinical_risk_score=clinical_score.get("clinical_risk_score"),
        confidence_note=confidence_note,
        abnormal_markers=clinical_score.get("warnings", []),
        markers_checked=clinical_score.get("provided_count", 0),
    )


def _error_result(disease, error_msg):
    return PredictionResult(
        disease=disease, risk_level="Unknown",
        probability=0.0, percentage=0,
        recommendation=f"Prediction failed: {error_msg}.",
        features_used=[], model_available=False,
        raw_model_probability=None, clinical_risk_score=None,
        confidence_note="Prediction could not be completed.",
        abnormal_markers=[], markers_checked=0,
    )


def predict_kidney(model_bundle, data):
    try:
        clinical = compute_clinical_score(data, KIDNEY_KEY_MARKERS)
        return _run_prediction("Kidney Disease", model_bundle, map_kidney_features(data), clinical, get_kidney_features_used(data))
    except Exception as e:
        return _error_result("Kidney Disease", str(e))


def predict_heart(model_bundle, data):
    try:
        clinical = compute_clinical_score(data, HEART_KEY_MARKERS)
        return _run_prediction("Heart Disease", model_bundle, map_heart_features(data), clinical, get_heart_features_used(data))
    except Exception as e:
        return _error_result("Heart Disease", str(e))


def predict_liver(model_bundle, data):
    try:
        clinical = compute_clinical_score(data, LIVER_KEY_MARKERS)
        return _run_prediction("Liver Disease", model_bundle, map_liver_features(data), clinical, get_liver_features_used(data))
    except Exception as e:
        return _error_result("Liver Disease", str(e))


def predict_diabetes(model_bundle, data):
    try:
        clinical = compute_clinical_score(data, DIABETES_KEY_MARKERS)
        return _run_prediction("Diabetes", model_bundle, map_diabetes_features(data), clinical, get_diabetes_features_used(data))
    except Exception as e:
        return _error_result("Diabetes", str(e))


def run_all_predictions(models: dict, data: MasterInputSchema) -> list:
    results = []
    disease_map = {
        "kidney":   ("Kidney Disease", predict_kidney),
        "heart":    ("Heart Disease",  predict_heart),
        "liver":    ("Liver Disease",  predict_liver),
        "diabetes": ("Diabetes",       predict_diabetes),
    }
    for key, (disease_name, fn) in disease_map.items():
        if models.get(key):
            results.append(fn(models[key], data))
        else:
            results.append(PredictionResult(
                disease=disease_name, risk_level="Unavailable",
                probability=0, percentage=0,
                recommendation=f"Add {key}_model.pkl to backend/models/.",
                features_used=[], model_available=False,
                raw_model_probability=None, clinical_risk_score=None,
                confidence_note="Model not available.",
                abnormal_markers=[], markers_checked=0,
            ))
    return results



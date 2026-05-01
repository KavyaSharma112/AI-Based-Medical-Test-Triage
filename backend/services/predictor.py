"""
Prediction Service
==================
This module contains the prediction logic for each disease.

For each model it:
  1. Maps the master schema to model-specific features
  2. Applies scaling if the model needs it (scaler stored in pkl)
  3. Gets probability from model.predict_proba()
  4. Converts probability → risk level (Low / Moderate / High)
  5. Returns a recommendation based on risk level

─────────────────────────────────────────────────────────────
RISK LEVEL THRESHOLDS
  Low:      probability < 0.40
  Moderate: probability 0.40–0.65
  High:     probability > 0.65
─────────────────────────────────────────────────────────────
"""

import numpy as np
from schemas.input_schema import MasterInputSchema, PredictionResult
from services.feature_mapper import (
    map_kidney_features, get_kidney_features_used,
    map_heart_features, get_heart_features_used,
    map_liver_features, get_liver_features_used,
    map_diabetes_features, get_diabetes_features_used,
)


# ─── Risk Level Logic ─────────────────────────────────────────────────────────

def probability_to_risk(prob: float) -> str:
    """Convert 0-1 probability to a human-readable risk level."""
    if prob < 0.40:
        return "Low"
    elif prob < 0.65:
        return "Moderate"
    else:
        return "High"


def get_recommendation(disease: str, risk_level: str) -> str:
    """Return a simple, safe recommendation based on disease + risk level."""
    recommendations = {
        "Kidney Disease": {
            "Low": "Your kidney indicators appear within normal range. Stay hydrated and maintain annual check-ups.",
            "Moderate": "Some kidney indicators are concerning. Reduce salt intake, stay hydrated, and consult a nephrologist.",
            "High": "Multiple kidney risk factors detected. Please consult a nephrologist promptly for further evaluation.",
        },
        "Heart Disease": {
            "Low": "Your cardiac indicators appear within normal range. Maintain a heart-healthy diet and regular exercise.",
            "Moderate": "Some cardiac risk factors are present. Consider lifestyle changes and consult a cardiologist.",
            "High": "Significant cardiac risk factors detected. Please consult a cardiologist promptly for evaluation.",
        },
        "Liver Disease": {
            "Low": "Your liver function indicators appear within normal range. Limit alcohol and maintain a healthy diet.",
            "Moderate": "Some liver function markers are elevated. Avoid alcohol, reduce fatty foods, and consult a hepatologist.",
            "High": "Multiple liver function abnormalities detected. Please consult a hepatologist promptly.",
        },
        "Diabetes": {
            "Low": "Your metabolic indicators suggest low diabetes risk. Maintain a balanced diet and regular exercise.",
            "Moderate": "Some metabolic risk factors are present. Monitor blood sugar, reduce sugary foods, and consult a doctor.",
            "High": "Significant diabetes risk factors detected. Please consult an endocrinologist for glucose testing.",
        },
    }
    return recommendations.get(disease, {}).get(risk_level, "Please consult a healthcare professional.")


# ─── Individual Prediction Functions ──────────────────────────────────────────

def predict_kidney(model_bundle: dict, data: MasterInputSchema) -> PredictionResult:
    """Run the kidney disease prediction model."""
    try:
        model = model_bundle["model"]
        scaler = model_bundle.get("scaler")

        # Get feature array
        X = map_kidney_features(data)

        # Apply scaling if scaler exists
        if scaler is not None:
            X = scaler.transform(X)

        # Get probability of disease (class 1)
        prob = float(model.predict_proba(X)[0][1])
        risk = probability_to_risk(prob)

        return PredictionResult(
            disease="Kidney Disease",
            risk_level=risk,
            probability=round(prob, 4),
            percentage=int(prob * 100),
            recommendation=get_recommendation("Kidney Disease", risk),
            features_used=get_kidney_features_used(data),
            model_available=True,
        )
    except Exception as e:
        return PredictionResult(
            disease="Kidney Disease",
            risk_level="Unknown",
            probability=0.0,
            percentage=0,
            recommendation=f"Prediction failed: {str(e)}. Please check your input values.",
            features_used=[],
            model_available=False,
        )


def predict_heart(model_bundle: dict, data: MasterInputSchema) -> PredictionResult:
    """Run the heart disease prediction model."""
    try:
        model = model_bundle["model"]
        scaler = model_bundle.get("scaler")

        X = map_heart_features(data)

        # Heart model: notebook showed scaler only applied to numeric columns
        # For Random Forest (no scaling needed), scaler may be None
        if scaler is not None:
            X = scaler.transform(X)

        prob = float(model.predict_proba(X)[0][1])
        risk = probability_to_risk(prob)

        return PredictionResult(
            disease="Heart Disease",
            risk_level=risk,
            probability=round(prob, 4),
            percentage=int(prob * 100),
            recommendation=get_recommendation("Heart Disease", risk),
            features_used=get_heart_features_used(data),
            model_available=True,
        )
    except Exception as e:
        return PredictionResult(
            disease="Heart Disease",
            risk_level="Unknown",
            probability=0.0,
            percentage=0,
            recommendation=f"Prediction failed: {str(e)}. Please check your input values.",
            features_used=[],
            model_available=False,
        )


def predict_liver(model_bundle: dict, data: MasterInputSchema) -> PredictionResult:
    """Run the liver disease prediction model."""
    try:
        model = model_bundle["model"]
        scaler = model_bundle.get("scaler")

        X = map_liver_features(data)

        if scaler is not None:
            X = scaler.transform(X)

        prob = float(model.predict_proba(X)[0][1])
        risk = probability_to_risk(prob)

        return PredictionResult(
            disease="Liver Disease",
            risk_level=risk,
            probability=round(prob, 4),
            percentage=int(prob * 100),
            recommendation=get_recommendation("Liver Disease", risk),
            features_used=get_liver_features_used(data),
            model_available=True,
        )
    except Exception as e:
        return PredictionResult(
            disease="Liver Disease",
            risk_level="Unknown",
            probability=0.0,
            percentage=0,
            recommendation=f"Prediction failed: {str(e)}. Please check your input values.",
            features_used=[],
            model_available=False,
        )


def predict_diabetes(model_bundle: dict, data: MasterInputSchema) -> PredictionResult:
    """Run the diabetes prediction model."""
    try:
        model = model_bundle["model"]
        scaler = model_bundle.get("scaler")

        X = map_diabetes_features(data)

        if scaler is not None:
            X = scaler.transform(X)

        prob = float(model.predict_proba(X)[0][1])
        risk = probability_to_risk(prob)

        return PredictionResult(
            disease="Diabetes",
            risk_level=risk,
            probability=round(prob, 4),
            percentage=int(prob * 100),
            recommendation=get_recommendation("Diabetes", risk),
            features_used=get_diabetes_features_used(data),
            model_available=True,
        )
    except Exception as e:
        return PredictionResult(
            disease="Diabetes",
            risk_level="Unknown",
            probability=0.0,
            percentage=0,
            recommendation=f"Prediction failed: {str(e)}. Please check your input values.",
            features_used=[],
            model_available=False,
        )


# ─── Master Prediction Function ───────────────────────────────────────────────

def run_all_predictions(models: dict, data: MasterInputSchema) -> list[PredictionResult]:
    """
    Run all 4 models and return a list of PredictionResult objects.
    Even if one model fails (missing pkl), the others still run.
    """
    results = []

    # Kidney
    if models.get("kidney"):
        results.append(predict_kidney(models["kidney"], data))
    else:
        results.append(PredictionResult(
            disease="Kidney Disease", risk_level="Unavailable",
            probability=0, percentage=0,
            recommendation="Kidney model not loaded. Add kidney_model.pkl to backend/models/.",
            features_used=[], model_available=False,
        ))

    # Heart
    if models.get("heart"):
        results.append(predict_heart(models["heart"], data))
    else:
        results.append(PredictionResult(
            disease="Heart Disease", risk_level="Unavailable",
            probability=0, percentage=0,
            recommendation="Heart model not loaded. Add heart_model.pkl to backend/models/.",
            features_used=[], model_available=False,
        ))

    # Liver
    if models.get("liver"):
        results.append(predict_liver(models["liver"], data))
    else:
        results.append(PredictionResult(
            disease="Liver Disease", risk_level="Unavailable",
            probability=0, percentage=0,
            recommendation="Liver model not loaded. Add liver_model.pkl to backend/models/.",
            features_used=[], model_available=False,
        ))

    # Diabetes
    if models.get("diabetes"):
        results.append(predict_diabetes(models["diabetes"], data))
    else:
        results.append(PredictionResult(
            disease="Diabetes", risk_level="Unavailable",
            probability=0, percentage=0,
            recommendation="Diabetes model not loaded. Add diabetes_model.pkl to backend/models/.",
            features_used=[], model_available=False,
        ))

    return results

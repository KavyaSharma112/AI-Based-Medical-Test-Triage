"""
Feature Mapping Layer
=====================
This is the CORE of the triage system.

Each ML model was trained on a specific dataset with specific column names
and a specific order. This module maps the unified MasterInputSchema to
each model's expected input format.

Key concepts:
  1. FEATURE ORDER matters — sklearn models expect features in the exact
     same column order they were trained on.
  2. MISSING VALUES are filled with sensible defaults (dataset means or
     clinically safe neutral values).
  3. ENCODING: Some models expect encoded categorical values (e.g., 0/1
     for yes/no). We handle those mappings here.

─────────────────────────────────────────────────────────────────────────
HOW TO READ THIS FILE
─────────────────────────────────────────────────────────────────────────
Each model has:
  - FEATURE_ORDER: list of feature names in the order the model was trained
  - DEFAULTS: fallback values for missing features
  - A mapper function: takes MasterInputSchema → numpy array

The mapper functions are imported and called by the prediction services.
─────────────────────────────────────────────────────────────────────────
"""

import numpy as np
from schemas.input_schema import MasterInputSchema


# ══════════════════════════════════════════════════════════════════════════════
# KIDNEY DISEASE — Trained on kidney_full.csv (CKD dataset)
# Features from UCI Chronic Kidney Disease dataset
# ══════════════════════════════════════════════════════════════════════════════

KIDNEY_FEATURE_ORDER = [
    "age", "bp", "sg", "al", "su", "rbc", "pc", "pcc", "ba",
    "bgr", "bu", "sc", "sod", "pot", "hemo", "pcv", "wbcc", "rbcc",
    "htn", "dm", "cad", "appet", "pe", "ane"
]

# Default values = approximate column means from the CKD dataset
KIDNEY_DEFAULTS = {
    "age": 51.0,
    "bp": 76.0,     # blood pressure
    "sg": 1.017,    # specific gravity
    "al": 1.0,      # albumin
    "su": 0.0,      # sugar
    "rbc": 0.0,     # red blood cells (0=normal, 1=abnormal)
    "pc": 0.0,      # pus cell (0=normal, 1=abnormal)
    "pcc": 0.0,     # pus cell clumps
    "ba": 0.0,      # bacteria
    "bgr": 148.0,   # blood glucose random
    "bu": 53.0,     # blood urea
    "sc": 3.0,      # serum creatinine
    "sod": 137.0,   # sodium
    "pot": 4.6,     # potassium
    "hemo": 12.5,   # haemoglobin
    "pcv": 38.0,    # packed cell volume
    "wbcc": 8400.0, # white blood cell count
    "rbcc": 4.7,    # red blood cell count
    "htn": 0,       # hypertension
    "dm": 0,        # diabetes mellitus
    "cad": 0,       # coronary artery disease
    "appet": 1,     # appetite (1=good)
    "pe": 0,        # pedal edema
    "ane": 0,       # anemia
}


def map_kidney_features(data: MasterInputSchema) -> np.ndarray:
    """Map master schema to the 24 kidney disease features."""
    # Build the feature dict using user data where available, defaults otherwise
    features = {
        "age":  data.age   if data.age   is not None else KIDNEY_DEFAULTS["age"],
        "bp":   data.blood_pressure if data.blood_pressure is not None else KIDNEY_DEFAULTS["bp"],
        "sg":   data.specific_gravity if data.specific_gravity is not None else KIDNEY_DEFAULTS["sg"],
        "al":   data.albumin if data.albumin is not None else KIDNEY_DEFAULTS["al"],
        "su":   data.sugar  if data.sugar  is not None else KIDNEY_DEFAULTS["su"],
        "rbc":  data.red_blood_cells if data.red_blood_cells is not None else KIDNEY_DEFAULTS["rbc"],
        "pc":   data.pus_cell if data.pus_cell is not None else KIDNEY_DEFAULTS["pc"],
        "pcc":  data.pus_cell_clumps if data.pus_cell_clumps is not None else KIDNEY_DEFAULTS["pcc"],
        "ba":   data.bacteria if data.bacteria is not None else KIDNEY_DEFAULTS["ba"],
        "bgr":  data.blood_glucose_random if data.blood_glucose_random is not None else KIDNEY_DEFAULTS["bgr"],
        "bu":   data.blood_urea if data.blood_urea is not None else KIDNEY_DEFAULTS["bu"],
        "sc":   data.serum_creatinine if data.serum_creatinine is not None else KIDNEY_DEFAULTS["sc"],
        "sod":  data.sodium if data.sodium is not None else KIDNEY_DEFAULTS["sod"],
        "pot":  data.potassium if data.potassium is not None else KIDNEY_DEFAULTS["pot"],
        "hemo": data.haemoglobin if data.haemoglobin is not None else KIDNEY_DEFAULTS["hemo"],
        "pcv":  data.packed_cell_volume if data.packed_cell_volume is not None else KIDNEY_DEFAULTS["pcv"],
        "wbcc": data.white_blood_cell_count if data.white_blood_cell_count is not None else KIDNEY_DEFAULTS["wbcc"],
        "rbcc": data.red_blood_cell_count if data.red_blood_cell_count is not None else KIDNEY_DEFAULTS["rbcc"],
        "htn":  data.hypertension if data.hypertension is not None else KIDNEY_DEFAULTS["htn"],
        "dm":   data.diabetes_mellitus if data.diabetes_mellitus is not None else KIDNEY_DEFAULTS["dm"],
        "cad":  data.coronary_artery_disease if data.coronary_artery_disease is not None else KIDNEY_DEFAULTS["cad"],
        "appet": data.appetite if data.appetite is not None else KIDNEY_DEFAULTS["appet"],
        "pe":   data.peda_edema if data.peda_edema is not None else KIDNEY_DEFAULTS["pe"],
        "ane":  data.aanemia if data.aanemia is not None else KIDNEY_DEFAULTS["ane"],
    }
    # Return as 2D array (1 sample, 24 features) in the correct order
    return np.array([[features[f] for f in KIDNEY_FEATURE_ORDER]], dtype=float)


def get_kidney_features_used(data: MasterInputSchema) -> list:
    """Return list of kidney features that were actually provided by user."""
    mapping = {
        "age": data.age, "blood_pressure": data.blood_pressure,
        "specific_gravity": data.specific_gravity, "albumin": data.albumin,
        "sugar": data.sugar, "blood_glucose_random": data.blood_glucose_random,
        "blood_urea": data.blood_urea, "serum_creatinine": data.serum_creatinine,
        "haemoglobin": data.haemoglobin,
    }
    return [k for k, v in mapping.items() if v is not None]


# ══════════════════════════════════════════════════════════════════════════════
# HEART DISEASE — Trained on UCI Heart Disease dataset
# ══════════════════════════════════════════════════════════════════════════════

HEART_FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalch", "exang", "oldpeak", "slope", "ca", "thal"
]

HEART_DEFAULTS = {
    "age": 54.0,
    "sex": 1,           # 0=female, 1=male
    "cp": 0,            # chest pain type (0=asymptomatic is most common in dataset)
    "trestbps": 131.0,  # resting BP
    "chol": 247.0,      # cholesterol
    "fbs": 0,           # fasting blood sugar <= 120
    "restecg": 1,       # normal
    "thalch": 149.0,    # max heart rate
    "exang": 0,         # no exercise angina
    "oldpeak": 1.0,     # ST depression
    "slope": 1,         # flat
    "ca": 0.0,          # 0 major vessels
    "thal": 1,          # normal
}


def map_heart_features(data: MasterInputSchema) -> np.ndarray:
    """Map master schema to the 13 heart disease features."""
    # Use sex or gender (they mean the same, different field names)
    sex_val = data.sex if data.sex is not None else (
              data.gender if data.gender is not None else HEART_DEFAULTS["sex"])

    features = {
        "age":      data.age if data.age is not None else HEART_DEFAULTS["age"],
        "sex":      sex_val,
        "cp":       data.chest_pain_type if data.chest_pain_type is not None else HEART_DEFAULTS["cp"],
        "trestbps": data.resting_blood_pressure if data.resting_blood_pressure is not None else (
                    data.blood_pressure if data.blood_pressure is not None else HEART_DEFAULTS["trestbps"]),
        "chol":     data.cholesterol if data.cholesterol is not None else HEART_DEFAULTS["chol"],
        "fbs":      data.fasting_blood_sugar if data.fasting_blood_sugar is not None else HEART_DEFAULTS["fbs"],
        "restecg":  data.resting_ecg if data.resting_ecg is not None else HEART_DEFAULTS["restecg"],
        "thalch":   data.max_heart_rate if data.max_heart_rate is not None else HEART_DEFAULTS["thalch"],
        "exang":    data.exercise_angina if data.exercise_angina is not None else HEART_DEFAULTS["exang"],
        "oldpeak":  data.st_depression if data.st_depression is not None else HEART_DEFAULTS["oldpeak"],
        "slope":    data.st_slope if data.st_slope is not None else HEART_DEFAULTS["slope"],
        "ca":       data.num_vessels if data.num_vessels is not None else HEART_DEFAULTS["ca"],
        "thal":     data.thalassemia if data.thalassemia is not None else HEART_DEFAULTS["thal"],
    }
    return np.array([[features[f] for f in HEART_FEATURE_ORDER]], dtype=float)


def get_heart_features_used(data: MasterInputSchema) -> list:
    mapping = {
        "age": data.age, "sex/gender": data.sex or data.gender,
        "chest_pain_type": data.chest_pain_type, "cholesterol": data.cholesterol,
        "resting_blood_pressure": data.resting_blood_pressure,
        "max_heart_rate": data.max_heart_rate, "st_depression": data.st_depression,
    }
    return [k for k, v in mapping.items() if v is not None]


# ══════════════════════════════════════════════════════════════════════════════
# LIVER DISEASE — Trained on ILPD (Indian Liver Patient Dataset)
# ══════════════════════════════════════════════════════════════════════════════

LIVER_FEATURE_ORDER = [
    "Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin",
    "Alkaline_Phosphotase", "Alamine_Aminotransferase",
    "Aspartate_Aminotransferase", "Total_Protiens",
    "Albumin", "Albumin_and_Globulin_Ratio"
]

LIVER_DEFAULTS = {
    "Age": 44.0,
    "Gender": 1,                    # 1=Male (more common in dataset)
    "Total_Bilirubin": 3.3,
    "Direct_Bilirubin": 1.5,
    "Alkaline_Phosphotase": 290.0,
    "Alamine_Aminotransferase": 80.0,
    "Aspartate_Aminotransferase": 109.0,
    "Total_Protiens": 6.5,
    "Albumin": 3.1,
    "Albumin_and_Globulin_Ratio": 0.95,
}


def map_liver_features(data: MasterInputSchema) -> np.ndarray:
    """Map master schema to the 10 liver disease features."""
    # Gender: notebook used LabelEncoder on Male/Female → Male=1, Female=0
    gender_val = data.gender if data.gender is not None else (
                 data.sex if data.sex is not None else LIVER_DEFAULTS["Gender"])

    # Albumin: kidney model uses it as urine albumin (0-5 scale)
    # Liver model uses serum albumin (g/dL, typically 3-5)
    # We use the same field but it's context-dependent
    albumin_val = data.albumin if (data.albumin is not None and data.albumin > 5) else LIVER_DEFAULTS["Albumin"]

    features = {
        "Age":                      data.age if data.age is not None else LIVER_DEFAULTS["Age"],
        "Gender":                   gender_val,
        "Total_Bilirubin":          data.total_bilirubin if data.total_bilirubin is not None else LIVER_DEFAULTS["Total_Bilirubin"],
        "Direct_Bilirubin":         data.direct_bilirubin if data.direct_bilirubin is not None else LIVER_DEFAULTS["Direct_Bilirubin"],
        "Alkaline_Phosphotase":     data.alkaline_phosphotase if data.alkaline_phosphotase is not None else LIVER_DEFAULTS["Alkaline_Phosphotase"],
        "Alamine_Aminotransferase": data.alamine_aminotransferase if data.alamine_aminotransferase is not None else LIVER_DEFAULTS["Alamine_Aminotransferase"],
        "Aspartate_Aminotransferase": data.aspartate_aminotransferase if data.aspartate_aminotransferase is not None else LIVER_DEFAULTS["Aspartate_Aminotransferase"],
        "Total_Protiens":           data.total_proteins if data.total_proteins is not None else LIVER_DEFAULTS["Total_Protiens"],
        "Albumin":                  albumin_val,
        "Albumin_and_Globulin_Ratio": data.albumin_globulin_ratio if data.albumin_globulin_ratio is not None else LIVER_DEFAULTS["Albumin_and_Globulin_Ratio"],
    }
    return np.array([[features[f] for f in LIVER_FEATURE_ORDER]], dtype=float)


def get_liver_features_used(data: MasterInputSchema) -> list:
    mapping = {
        "age": data.age, "total_bilirubin": data.total_bilirubin,
        "direct_bilirubin": data.direct_bilirubin,
        "alkaline_phosphotase": data.alkaline_phosphotase,
        "alamine_aminotransferase (ALT)": data.alamine_aminotransferase,
        "aspartate_aminotransferase (AST)": data.aspartate_aminotransferase,
        "total_proteins": data.total_proteins, "albumin": data.albumin,
        "albumin_globulin_ratio": data.albumin_globulin_ratio,
    }
    return [k for k, v in mapping.items() if v is not None]


# ══════════════════════════════════════════════════════════════════════════════
# DIABETES — Trained on Pima Indians Diabetes dataset
# ══════════════════════════════════════════════════════════════════════════════

DIABETES_FEATURE_ORDER = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]

DIABETES_DEFAULTS = {
    "Pregnancies": 3.8,
    "Glucose": 120.9,      # mean of dataset (after replacing 0s)
    "BloodPressure": 69.1,
    "SkinThickness": 20.5,
    "Insulin": 79.8,       # mean after replacing 0s
    "BMI": 32.0,
    "DiabetesPedigreeFunction": 0.47,
    "Age": 33.0,
}


def map_diabetes_features(data: MasterInputSchema) -> np.ndarray:
    """Map master schema to the 8 diabetes features."""
    features = {
        "Pregnancies":              data.pregnancies if data.pregnancies is not None else DIABETES_DEFAULTS["Pregnancies"],
        "Glucose":                  data.glucose if data.glucose is not None else (
                                    data.blood_glucose_random if data.blood_glucose_random is not None else DIABETES_DEFAULTS["Glucose"]),
        "BloodPressure":            data.blood_pressure if data.blood_pressure is not None else DIABETES_DEFAULTS["BloodPressure"],
        "SkinThickness":            data.skin_thickness if data.skin_thickness is not None else DIABETES_DEFAULTS["SkinThickness"],
        "Insulin":                  data.insulin if data.insulin is not None else DIABETES_DEFAULTS["Insulin"],
        "BMI":                      data.bmi if data.bmi is not None else DIABETES_DEFAULTS["BMI"],
        "DiabetesPedigreeFunction": data.diabetes_pedigree_function if data.diabetes_pedigree_function is not None else DIABETES_DEFAULTS["DiabetesPedigreeFunction"],
        "Age":                      data.age if data.age is not None else DIABETES_DEFAULTS["Age"],
    }
    return np.array([[features[f] for f in DIABETES_FEATURE_ORDER]], dtype=float)


def get_diabetes_features_used(data: MasterInputSchema) -> list:
    mapping = {
        "glucose": data.glucose or data.blood_glucose_random,
        "blood_pressure": data.blood_pressure,
        "bmi": data.bmi, "insulin": data.insulin,
        "age": data.age, "pregnancies": data.pregnancies,
        "skin_thickness": data.skin_thickness,
        "diabetes_pedigree_function": data.diabetes_pedigree_function,
    }
    return [k for k, v in mapping.items() if v is not None]

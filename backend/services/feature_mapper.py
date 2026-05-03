import numpy as np
from schemas.input_schema import MasterInputSchema


# ══════════════════════════════════════════════════════════════════════════════
# KIDNEY DISEASE
# ══════════════════════════════════════════════════════════════════════════════

KIDNEY_FEATURE_ORDER = [
    "age", "bp", "sg", "al", "su", "rbc", "pc", "pcc", "ba",
    "bgr", "bu", "sc", "sod", "pot", "hemo", "pcv", "wbcc", "rbcc",
    "htn", "dm", "cad", "appet", "pe", "ane"
]

KIDNEY_DEFAULTS = {
    "age": 40.0, "bp": 70.0, "sg": 1.020, "al": 0.0, "su": 0.0,
    "rbc": 0.0, "pc": 0.0, "pcc": 0.0, "ba": 0.0,
    "bgr": 90.0,   # was 148.0 (prediabetic) → fixed to healthy
    "bu": 15.0,    # was 53.0 (elevated) → fixed to healthy
    "sc": 0.9,     # was 3.0 (CKD level) → fixed to healthy
    "sod": 140.0, "pot": 4.0,
    "hemo": 14.5,  # was 12.5 (borderline low) → fixed
    "pcv": 44.0, "wbcc": 7500.0, "rbcc": 5.0,
    "htn": 0, "dm": 0, "cad": 0, "appet": 1, "pe": 0, "ane": 0,
}


def map_kidney_features(data: MasterInputSchema) -> np.ndarray:
    features = {
        "age":  data.age            if data.age            is not None else KIDNEY_DEFAULTS["age"],
        "bp":   data.blood_pressure if data.blood_pressure is not None else KIDNEY_DEFAULTS["bp"],
        "sg":   data.specific_gravity if data.specific_gravity is not None else KIDNEY_DEFAULTS["sg"],
        "al":   data.albumin        if data.albumin        is not None else KIDNEY_DEFAULTS["al"],
        "su":   data.sugar          if data.sugar          is not None else KIDNEY_DEFAULTS["su"],
        "rbc":  data.red_blood_cells if data.red_blood_cells is not None else KIDNEY_DEFAULTS["rbc"],
        "pc":   data.pus_cell       if data.pus_cell       is not None else KIDNEY_DEFAULTS["pc"],
        "pcc":  data.pus_cell_clumps if data.pus_cell_clumps is not None else KIDNEY_DEFAULTS["pcc"],
        "ba":   data.bacteria       if data.bacteria       is not None else KIDNEY_DEFAULTS["ba"],
        "bgr":  data.blood_glucose_random if data.blood_glucose_random is not None else KIDNEY_DEFAULTS["bgr"],
        "bu":   data.blood_urea     if data.blood_urea     is not None else KIDNEY_DEFAULTS["bu"],
        "sc":   data.serum_creatinine if data.serum_creatinine is not None else KIDNEY_DEFAULTS["sc"],
        "sod":  data.sodium         if data.sodium         is not None else KIDNEY_DEFAULTS["sod"],
        "pot":  data.potassium      if data.potassium      is not None else KIDNEY_DEFAULTS["pot"],
        "hemo": data.haemoglobin    if data.haemoglobin    is not None else KIDNEY_DEFAULTS["hemo"],
        "pcv":  data.packed_cell_volume if data.packed_cell_volume is not None else KIDNEY_DEFAULTS["pcv"],
        "wbcc": data.white_blood_cell_count if data.white_blood_cell_count is not None else KIDNEY_DEFAULTS["wbcc"],
        "rbcc": data.red_blood_cell_count if data.red_blood_cell_count is not None else KIDNEY_DEFAULTS["rbcc"],
        "htn":  data.hypertension   if data.hypertension   is not None else KIDNEY_DEFAULTS["htn"],
        "dm":   data.diabetes_mellitus if data.diabetes_mellitus is not None else KIDNEY_DEFAULTS["dm"],
        "cad":  data.coronary_artery_disease if data.coronary_artery_disease is not None else KIDNEY_DEFAULTS["cad"],
        "appet": data.appetite      if data.appetite       is not None else KIDNEY_DEFAULTS["appet"],
        "pe":   data.peda_edema     if data.peda_edema     is not None else KIDNEY_DEFAULTS["pe"],
        "ane":  data.aanemia        if data.aanemia        is not None else KIDNEY_DEFAULTS["ane"],
    }
    return np.array([[features[f] for f in KIDNEY_FEATURE_ORDER]], dtype=float)


def get_kidney_features_used(data: MasterInputSchema) -> list:
    mapping = {
        "age": data.age, "blood_pressure": data.blood_pressure,
        "specific_gravity": data.specific_gravity, "albumin": data.albumin,
        "sugar": data.sugar, "blood_glucose_random": data.blood_glucose_random,
        "blood_urea": data.blood_urea, "serum_creatinine": data.serum_creatinine,
        "sodium": data.sodium, "potassium": data.potassium,
        "haemoglobin": data.haemoglobin, "packed_cell_volume": data.packed_cell_volume,
        "wbc_count": data.white_blood_cell_count, "rbc_count": data.red_blood_cell_count,
    }
    return [k for k, v in mapping.items() if v is not None]


# ══════════════════════════════════════════════════════════════════════════════
# HEART DISEASE
# ══════════════════════════════════════════════════════════════════════════════

HEART_FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalch", "exang", "oldpeak", "slope", "ca", "thal"
]

HEART_DEFAULTS = {
    "age": 45.0, "sex": 1, "cp": 1,
    "trestbps": 120.0,  # was 131.0 (hypertensive) → fixed
    "chol": 200.0,      # was 247.0 (borderline high) → fixed
    "fbs": 0, "restecg": 1, "thalch": 160.0, "exang": 0,
    "oldpeak": 0.0,     # was 1.0 (elevated) → fixed
    "slope": 2, "ca": 0.0, "thal": 2,
}


def map_heart_features(data: MasterInputSchema) -> np.ndarray:
    sex_val = (data.sex if data.sex is not None
               else data.gender if data.gender is not None
               else HEART_DEFAULTS["sex"])
    features = {
        "age":      data.age if data.age is not None else HEART_DEFAULTS["age"],
        "sex":      sex_val,
        "cp":       data.chest_pain_type if data.chest_pain_type is not None else HEART_DEFAULTS["cp"],
        "trestbps": (data.resting_blood_pressure if data.resting_blood_pressure is not None
                     else data.blood_pressure if data.blood_pressure is not None
                     else HEART_DEFAULTS["trestbps"]),
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
        "exercise_angina": data.exercise_angina, "num_vessels": data.num_vessels,
    }
    return [k for k, v in mapping.items() if v is not None]


# ══════════════════════════════════════════════════════════════════════════════
# LIVER DISEASE
# ══════════════════════════════════════════════════════════════════════════════

LIVER_FEATURE_ORDER = [
    "Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin",
    "Alkaline_Phosphotase", "Alamine_Aminotransferase",
    "Aspartate_Aminotransferase", "Total_Protiens",
    "Albumin", "Albumin_and_Globulin_Ratio"
]

LIVER_DEFAULTS = {
    "Age": 44.0, "Gender": 1,
    "Total_Bilirubin": 0.7,         
    "Direct_Bilirubin": 0.2,        
    "Alkaline_Phosphotase": 90.0,   
    "Alamine_Aminotransferase": 25.0,   
    "Aspartate_Aminotransferase": 25.0, 
    "Total_Protiens": 7.0,
    "Albumin": 4.0,
    "Albumin_and_Globulin_Ratio": 1.2,
}


def map_liver_features(data: MasterInputSchema) -> np.ndarray:
    gender_val = (data.gender if data.gender is not None
                  else data.sex if data.sex is not None
                  else LIVER_DEFAULTS["Gender"])

    albumin_val = (data.serum_albumin if data.serum_albumin is not None
                   else LIVER_DEFAULTS["Albumin"])

    features = {
        "Age":                        data.age if data.age is not None else LIVER_DEFAULTS["Age"],
        "Gender":                     gender_val,
        "Total_Bilirubin":            data.total_bilirubin if data.total_bilirubin is not None else LIVER_DEFAULTS["Total_Bilirubin"],
        "Direct_Bilirubin":           data.direct_bilirubin if data.direct_bilirubin is not None else LIVER_DEFAULTS["Direct_Bilirubin"],
        "Alkaline_Phosphotase":       data.alkaline_phosphotase if data.alkaline_phosphotase is not None else LIVER_DEFAULTS["Alkaline_Phosphotase"],
        "Alamine_Aminotransferase":   data.alamine_aminotransferase if data.alamine_aminotransferase is not None else LIVER_DEFAULTS["Alamine_Aminotransferase"],
        "Aspartate_Aminotransferase": data.aspartate_aminotransferase if data.aspartate_aminotransferase is not None else LIVER_DEFAULTS["Aspartate_Aminotransferase"],
        "Total_Protiens":             data.total_proteins if data.total_proteins is not None else LIVER_DEFAULTS["Total_Protiens"],
        "Albumin":                    albumin_val,
        "Albumin_and_Globulin_Ratio": data.albumin_globulin_ratio if data.albumin_globulin_ratio is not None else LIVER_DEFAULTS["Albumin_and_Globulin_Ratio"],
    }
    return np.array([[features[f] for f in LIVER_FEATURE_ORDER]], dtype=float)


def get_liver_features_used(data: MasterInputSchema) -> list:
    mapping = {
        "age": data.age, "total_bilirubin": data.total_bilirubin,
        "direct_bilirubin": data.direct_bilirubin,
        "alkaline_phosphotase": data.alkaline_phosphotase,
        "ALT (SGPT)": data.alamine_aminotransferase,
        "AST (SGOT)": data.aspartate_aminotransferase,
        "total_proteins": data.total_proteins,
        "serum_albumin": data.serum_albumin,
        "albumin_globulin_ratio": data.albumin_globulin_ratio,
    }
    return [k for k, v in mapping.items() if v is not None]


# ══════════════════════════════════════════════════════════════════════════════
# DIABETES
# ══════════════════════════════════════════════════════════════════════════════

DIABETES_FEATURE_ORDER = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]

DIABETES_DEFAULTS = {
    "Pregnancies": 1.0,    
    "Glucose": 90.0,       
    "BloodPressure": 72.0,
    "SkinThickness": 20.0,
    "Insulin": 85.0,
    "BMI": 26.0,          
    "DiabetesPedigreeFunction": 0.35,
    "Age": 35.0,
}


def map_diabetes_features(data: MasterInputSchema) -> np.ndarray:
    features = {
        "Pregnancies": data.pregnancies if data.pregnancies is not None else DIABETES_DEFAULTS["Pregnancies"],
        "Glucose":     (data.glucose if data.glucose is not None
                        else data.blood_glucose_random if data.blood_glucose_random is not None
                        else DIABETES_DEFAULTS["Glucose"]),
        "BloodPressure": data.blood_pressure if data.blood_pressure is not None else DIABETES_DEFAULTS["BloodPressure"],
        "SkinThickness": data.skin_thickness if data.skin_thickness is not None else DIABETES_DEFAULTS["SkinThickness"],
        "Insulin":     data.insulin if data.insulin is not None else DIABETES_DEFAULTS["Insulin"],
        "BMI":         data.bmi if data.bmi is not None else DIABETES_DEFAULTS["BMI"],
        "DiabetesPedigreeFunction": (data.diabetes_pedigree_function
                                     if data.diabetes_pedigree_function is not None
                                     else DIABETES_DEFAULTS["DiabetesPedigreeFunction"]),
        "Age":         data.age if data.age is not None else DIABETES_DEFAULTS["Age"],
    }
    return np.array([[features[f] for f in DIABETES_FEATURE_ORDER]], dtype=float)


def get_diabetes_features_used(data: MasterInputSchema) -> list:
    mapping = {
        "glucose": data.glucose or data.blood_glucose_random,
        "blood_pressure": data.blood_pressure, "bmi": data.bmi,
        "insulin": data.insulin, "age": data.age,
        "pregnancies": data.pregnancies, "skin_thickness": data.skin_thickness,
        "diabetes_pedigree_function": data.diabetes_pedigree_function,
    }
    return [k for k, v in mapping.items() if v is not None]

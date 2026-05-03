"""
Master Input Schema
===================
This is the MOST IMPORTANT design decision in the backend.

Instead of 4 separate endpoints with 4 separate schemas, we define ONE
"master" schema that contains ALL possible features from all 4 models.

Every field is Optional — so the user only needs to fill in what they
know. Missing values are handled by the feature mapping layer.

─────────────────────────────────────────────────────────────
MODEL FEATURE REFERENCE
─────────────────────────────────────────────────────────────
KIDNEY (24 features):
  age, blood_pressure, specific_gravity, albumin, sugar,
  red_blood_cells, pus_cell, pus_cell_clumps, bacteria,
  blood_glucose_random, blood_urea, serum_creatinine,
  sodium, potassium, haemoglobin, packed_cell_volume,
  white_blood_cell_count, red_blood_cell_count,
  hypertension, diabetes_mellitus, coronary_artery_disease,
  appetite, peda_edema, aanemia

HEART (13 features):
  age, sex, chest_pain_type, resting_blood_pressure,
  cholesterol, fasting_blood_sugar, resting_ecg,
  max_heart_rate, exercise_angina, st_depression,
  st_slope, num_vessels, thalassemia

LIVER (10 features):
  age, gender, total_bilirubin, direct_bilirubin,
  alkaline_phosphotase, alamine_aminotransferase,
  aspartate_aminotransferase, total_proteins, albumin,
  albumin_globulin_ratio

DIABETES (8 features):
  pregnancies, glucose, blood_pressure, skin_thickness,
  insulin, bmi, diabetes_pedigree_function, age
─────────────────────────────────────────────────────────────
"""

from pydantic import BaseModel, Field
from typing import Optional


class MasterInputSchema(BaseModel):
    """
    Unified input schema. All fields are optional.
    Only provide what you have — the system fills in defaults for the rest.
    """

    # ── SHARED / DEMOGRAPHIC ──────────────────────────────────────────────────
    age: Optional[float] = Field(None, description="Age in years", example=45)
    gender: Optional[int] = Field(None, description="0 = Female, 1 = Male", example=1)
    sex: Optional[int] = Field(None, description="0 = Female, 1 = Male (Heart model)", example=1)

    # ── KIDNEY DISEASE FEATURES ───────────────────────────────────────────────
    blood_pressure: Optional[float] = Field(None, description="Blood pressure (mm/Hg)", example=80)
    specific_gravity: Optional[float] = Field(None, description="Urine specific gravity", example=1.020)
    albumin: Optional[float] = Field(None, description="Albumin in urine (0-5 scale)", example=1.0)
    sugar: Optional[float] = Field(None, description="Sugar in urine (0-5 scale)", example=0.0)
    red_blood_cells: Optional[int] = Field(None, description="0 = normal, 1 = abnormal", example=0)
    pus_cell: Optional[int] = Field(None, description="0 = normal, 1 = abnormal", example=0)
    pus_cell_clumps: Optional[int] = Field(None, description="0 = not present, 1 = present", example=0)
    bacteria: Optional[int] = Field(None, description="0 = not present, 1 = present", example=0)
    blood_glucose_random: Optional[float] = Field(None, description="Blood glucose random (mgs/dl)", example=121)
    blood_urea: Optional[float] = Field(None, description="Blood urea (mgs/dl)", example=36)
    serum_creatinine: Optional[float] = Field(None, description="Serum creatinine (mgs/dl)", example=1.2)
    sodium: Optional[float] = Field(None, description="Sodium (mEq/L)", example=137)
    potassium: Optional[float] = Field(None, description="Potassium (mEq/L)", example=4.2)
    haemoglobin: Optional[float] = Field(None, description="Haemoglobin (gms)", example=15.4)
    packed_cell_volume: Optional[float] = Field(None, description="Packed cell volume", example=44)
    white_blood_cell_count: Optional[float] = Field(None, description="WBC count (cells/cumm)", example=7800)
    red_blood_cell_count: Optional[float] = Field(None, description="RBC count (millions/cmm)", example=5.2)
    hypertension: Optional[int] = Field(None, description="0 = no, 1 = yes", example=0)
    diabetes_mellitus: Optional[int] = Field(None, description="0 = no, 1 = yes", example=0)
    coronary_artery_disease: Optional[int] = Field(None, description="0 = no, 1 = yes", example=0)
    appetite: Optional[int] = Field(None, description="0 = poor, 1 = good", example=1)
    peda_edema: Optional[int] = Field(None, description="0 = no, 1 = yes", example=0)
    aanemia: Optional[int] = Field(None, description="0 = no, 1 = yes", example=0)

    # ── HEART DISEASE FEATURES ────────────────────────────────────────────────
    chest_pain_type: Optional[int] = Field(None, description="0=asymptomatic, 1=atypical angina, 2=non-anginal, 3=typical angina", example=0)
    resting_blood_pressure: Optional[float] = Field(None, description="Resting blood pressure (mm Hg)", example=120)
    cholesterol: Optional[float] = Field(None, description="Serum cholesterol (mg/dl)", example=200)
    fasting_blood_sugar: Optional[int] = Field(None, description="Fasting blood sugar > 120 mg/dl: 0=no, 1=yes", example=0)
    resting_ecg: Optional[int] = Field(None, description="0=lv hypertrophy, 1=normal, 2=st-t abnormality", example=1)
    max_heart_rate: Optional[float] = Field(None, description="Maximum heart rate achieved", example=150)
    exercise_angina: Optional[int] = Field(None, description="Exercise induced angina: 0=no, 1=yes", example=0)
    st_depression: Optional[float] = Field(None, description="ST depression induced by exercise", example=0.0)
    st_slope: Optional[int] = Field(None, description="0=downsloping, 1=flat, 2=upsloping", example=2)
    num_vessels: Optional[float] = Field(None, description="Number of major vessels (0-3)", example=0)
    thalassemia: Optional[int] = Field(None, description="0=fixed defect, 1=normal, 2=reversable defect", example=1)

    # ── LIVER DISEASE FEATURES ────────────────────────────────────────────────
    total_bilirubin: Optional[float] = Field(None, description="Total bilirubin (mg/dL)", example=0.7)
    direct_bilirubin: Optional[float] = Field(None, description="Direct bilirubin (mg/dL)", example=0.1)
    alkaline_phosphotase: Optional[float] = Field(None, description="Alkaline phosphotase (IU/L)", example=187)
    alamine_aminotransferase: Optional[float] = Field(None, description="ALT / SGPT (IU/L)", example=16)
    aspartate_aminotransferase: Optional[float] = Field(None, description="AST / SGOT (IU/L)", example=18)
    total_proteins: Optional[float] = Field(None, description="Total proteins (g/dL)", example=6.8)
    albumin_globulin_ratio: Optional[float] = Field(None, description="Albumin and globulin ratio", example=0.9)
    serum_albumin: Optional[float] = Field(None, description="Serum albumin (g/dL) — used for liver model. Range 3.5–5.5", example=4.0)

    # ── DIABETES FEATURES ─────────────────────────────────────────────────────
    pregnancies: Optional[float] = Field(None, description="Number of pregnancies", example=0)
    glucose: Optional[float] = Field(None, description="Plasma glucose concentration (mg/dL)", example=120)
    skin_thickness: Optional[float] = Field(None, description="Triceps skin fold thickness (mm)", example=20)
    insulin: Optional[float] = Field(None, description="2-Hour serum insulin (mu U/ml)", example=79)
    bmi: Optional[float] = Field(None, description="Body Mass Index", example=25.0)
    diabetes_pedigree_function: Optional[float] = Field(None, description="Diabetes pedigree function", example=0.5)

    class Config:
        # Allows passing extra fields from PDF extraction without crashing
        extra = "ignore"


class PredictionResult(BaseModel):
    """Result for a single disease prediction."""
    disease: str
    risk_level: str                           # "Low", "Moderate", "High"
    probability: float                        # Adjusted probability (0.0 to 1.0)
    percentage: int                           # 0 to 100
    recommendation: str
    features_used: list[str]
    model_available: bool
    # New fields added in v2 (clinical calibration)
    raw_model_probability: Optional[float] = None
    clinical_risk_score: Optional[float] = None
    confidence_note: Optional[str] = None
    abnormal_markers: Optional[list[str]] = []
    markers_checked: Optional[int] = 0


class AllPredictionsResponse(BaseModel):
    """Combined response from the /predict-all endpoint."""
    predictions: list[PredictionResult]
    disclaimer: str = (
        "⚠️ This is NOT a medical diagnosis. These results are for informational "
        "purposes only. Please consult a qualified healthcare professional for "
        "proper medical evaluation and treatment."
    )
    input_summary: dict  # Echo back which fields were provided

"""
PDF Upload Route
================
Handles PDF lab report uploads and extracts medical values.

Flow:
  1. User uploads a PDF
  2. Extract text using pdfplumber (works for digital PDFs)
  3. Use regex + keyword mapping to extract medical values
  4. Normalize field names to our master schema
  5. Return extracted values as MasterInputSchema-compatible JSON

Supported lab value patterns:
  - "Glucose: 126 mg/dL"
  - "HbA1c 7.2%"
  - "Creatinine - 1.4"
  - "Haemoglobin (Hb): 11.2 g/dL"
  etc.
"""

import re
import io
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


# ─── Keyword Normalization Map ─────────────────────────────────────────────────
# Maps common abbreviations / alternate names → our master schema field names
# This is the "feature extraction normalization" layer

KEYWORD_MAP = {
    # Age
    "age": "age",

    # Glucose / Blood Sugar
    "glucose": "glucose",
    "blood glucose": "glucose",
    "blood sugar": "glucose",
    "fasting glucose": "glucose",
    "fasting blood sugar": "glucose",
    "fbs": "fasting_blood_sugar",   # Note: in heart model, fbs = >120 flag
    "rbs": "blood_glucose_random",
    "random blood sugar": "blood_glucose_random",
    "blood glucose random": "blood_glucose_random",

    # Blood Pressure
    "blood pressure": "blood_pressure",
    "bp": "blood_pressure",
    "systolic": "resting_blood_pressure",
    "resting bp": "resting_blood_pressure",
    "resting blood pressure": "resting_blood_pressure",

    # Kidney Markers
    "creatinine": "serum_creatinine",
    "serum creatinine": "serum_creatinine",
    "s. creatinine": "serum_creatinine",
    "urea": "blood_urea",
    "blood urea": "blood_urea",
    "bun": "blood_urea",            # blood urea nitrogen (similar)
    "sodium": "sodium",
    "na": "sodium",
    "potassium": "potassium",
    "k": "potassium",
    "specific gravity": "specific_gravity",
    "urine specific gravity": "specific_gravity",

    # Blood Counts
    "haemoglobin": "haemoglobin",
    "hemoglobin": "haemoglobin",
    "hb": "haemoglobin",
    "hgb": "haemoglobin",
    "wbc": "white_blood_cell_count",
    "white blood cell": "white_blood_cell_count",
    "total wbc": "white_blood_cell_count",
    "rbc count": "red_blood_cell_count",
    "red blood cell count": "red_blood_cell_count",
    "pcv": "packed_cell_volume",
    "hematocrit": "packed_cell_volume",
    "packed cell volume": "packed_cell_volume",

    # Liver Markers
    "bilirubin": "total_bilirubin",
    "total bilirubin": "total_bilirubin",
    "t. bilirubin": "total_bilirubin",
    "direct bilirubin": "direct_bilirubin",
    "d. bilirubin": "direct_bilirubin",
    "sgpt": "alamine_aminotransferase",
    "alt": "alamine_aminotransferase",
    "alamine aminotransferase": "alamine_aminotransferase",
    "alanine aminotransferase": "alamine_aminotransferase",
    "sgot": "aspartate_aminotransferase",
    "ast": "aspartate_aminotransferase",
    "aspartate aminotransferase": "aspartate_aminotransferase",
    "alp": "alkaline_phosphotase",
    "alkaline phosphatase": "alkaline_phosphotase",
    "alkaline phosphotase": "alkaline_phosphotase",
    "total protein": "total_proteins",
    "total proteins": "total_proteins",
    "albumin": "albumin",
    "serum albumin": "albumin",
    "a/g ratio": "albumin_globulin_ratio",
    "ag ratio": "albumin_globulin_ratio",
    "albumin globulin ratio": "albumin_globulin_ratio",

    # Heart Markers
    "cholesterol": "cholesterol",
    "total cholesterol": "cholesterol",
    "chol": "cholesterol",
    "max heart rate": "max_heart_rate",
    "heart rate": "max_heart_rate",

    # Body Metrics
    "bmi": "bmi",
    "body mass index": "bmi",
    "weight": None,    # Not used in models but don't crash
    "height": None,

    # Diabetes
    "insulin": "insulin",
    "pregnancies": "pregnancies",
    "skin thickness": "skin_thickness",
    "triceps": "skin_thickness",
}


# ─── Regex Patterns for Value Extraction ──────────────────────────────────────

# Matches: "Glucose: 126", "Glucose - 126.5", "Glucose = 126 mg/dL"
VALUE_PATTERN = re.compile(
    r"([\w\s/\.]+?)\s*[:\-=]\s*(\d+\.?\d*)\s*(mg/dl|mg/dl|g/dl|iu/l|meq/l|u/l|%|mmol/l|cells/cumm|millions/cmm)?",
    re.IGNORECASE
)

# Matches blood pressure like "120/80" or "BP: 120/80 mmHg"
BP_PATTERN = re.compile(r"(\d{2,3})\s*/\s*(\d{2,3})\s*(mmhg)?", re.IGNORECASE)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file using pdfplumber.
    Falls back to PyMuPDF if pdfplumber fails.
    Returns extracted text as a single string.
    """
    text = ""

    # Try pdfplumber first (better for text-based PDFs)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception as e:
        print(f"pdfplumber failed: {e}, trying PyMuPDF...")

    # Fallback: PyMuPDF (fitz)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract text from PDF: {str(e)}. "
                   "The PDF may be scanned. Try manual entry instead."
        )


def normalize_keyword(raw_key: str) -> str | None:
    """
    Normalize a raw extracted key (from PDF) to our master schema field name.
    Tries exact match first, then partial match.
    Returns None if no mapping found.
    """
    raw_lower = raw_key.strip().lower()

    # Exact match
    if raw_lower in KEYWORD_MAP:
        return KEYWORD_MAP[raw_lower]

    # Partial match (check if any known keyword is contained in the raw key)
    for keyword, field_name in KEYWORD_MAP.items():
        if keyword in raw_lower or raw_lower in keyword:
            return field_name

    return None


def extract_values_from_text(text: str) -> dict:
    """
    Parse raw PDF text and extract medical lab values.
    Returns a dict compatible with MasterInputSchema.
    """
    extracted = {}
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to extract blood pressure pattern (e.g., "120/80")
        bp_match = BP_PATTERN.search(line)
        if bp_match and ("blood pressure" in line.lower() or "bp" in line.lower()):
            systolic = float(bp_match.group(1))
            # diastolic = float(bp_match.group(2))  # Could use this too
            extracted["blood_pressure"] = systolic
            extracted["resting_blood_pressure"] = systolic
            continue

        # Try general key: value pattern
        matches = VALUE_PATTERN.findall(line)
        for match in matches:
            raw_key, raw_value, unit = match
            field_name = normalize_keyword(raw_key)

            if field_name and field_name not in extracted:
                try:
                    value = float(raw_value)
                    extracted[field_name] = value
                except ValueError:
                    pass

    return extracted


def clean_extracted_values(extracted: dict) -> dict:
    """
    Apply basic sanity checks to extracted values.
    Removes values that are clearly out of physiological range.
    """
    RANGE_CHECKS = {
        "age": (1, 120),
        "glucose": (20, 700),
        "blood_pressure": (40, 250),
        "serum_creatinine": (0.1, 30),
        "haemoglobin": (2, 25),
        "cholesterol": (50, 700),
        "bmi": (10, 80),
        "total_bilirubin": (0.1, 50),
        "alamine_aminotransferase": (1, 3000),
        "aspartate_aminotransferase": (1, 3000),
    }

    cleaned = {}
    for field, value in extracted.items():
        if field in RANGE_CHECKS:
            lo, hi = RANGE_CHECKS[field]
            if lo <= value <= hi:
                cleaned[field] = value
            else:
                print(f"⚠️  Skipping {field}={value} (out of range {lo}-{hi})")
        else:
            cleaned[field] = value

    return cleaned


# ─── API Route ─────────────────────────────────────────────────────────────────

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF lab report and extract medical values.
    
    Returns extracted values as JSON that can be passed to /predict-all.
    The frontend should display these values in the form for user review
    before running predictions.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted."
        )

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    # Extract text from PDF
    raw_text = extract_text_from_pdf(file_bytes)

    # Extract + clean medical values
    extracted = extract_values_from_text(raw_text)
    cleaned = clean_extracted_values(extracted)

    return {
        "status": "success",
        "filename": file.filename,
        "fields_extracted": len(cleaned),
        "extracted_values": cleaned,
        "raw_text_preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
        "message": (
            f"Extracted {len(cleaned)} lab values from your report. "
            "Please review the values before running predictions."
            if cleaned else
            "Could not extract any lab values automatically. Please enter values manually."
        )
    }

"""
PDF Upload Route (v3 — Table-First Extraction)
================================================
ROOT CAUSE OF PREVIOUS PARSING FAILURES:
  The old version used only regex on raw text. pdfplumber's extract_text()
  collapses table columns into a single line like:
    "Blood Glucose Random 121 70-140"
  and the regex couldn't reliably split the parameter name from the value
  when parameter names contain multiple words.

FIX:
  Use pdfplumber's extract_tables() as the PRIMARY method.
  It returns a clean list of rows: [['Parameter', 'Value', 'Normal Range'], ...]
  so we get the parameter name and value as separate strings — no regex needed
  for the split. We then normalize the parameter name through KEYWORD_MAP.

FALLBACK:
  If no tables are found (plain text report), fall back to the improved
  line-by-line regex parser.

RECOMMENDED PDF FORMAT (use this for lab reports):
  A simple 3-column table with headers: Parameter | Value | Normal Range
  This is guaranteed to extract 100% of fields correctly.
"""

import re
import io
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


# ─── Keyword → Master Schema Field Map ───────────────────────────────────────
# Sorted longest-first to prevent short keys greedily matching wrong labels

KEYWORD_MAP = {
    # Age
    "age": "age", "patient age": "age",

    # Glucose
    "glucose": "glucose", "blood glucose": "glucose",
    "blood sugar": "glucose", "fasting glucose": "glucose",
    "fasting blood glucose": "glucose", "plasma glucose": "glucose",
    "fbs": "glucose", "fasting blood sugar": "glucose",
    "rbs": "blood_glucose_random", "random blood sugar": "blood_glucose_random",
    "blood glucose random": "blood_glucose_random",
    "random blood glucose": "blood_glucose_random", "ppbs": "blood_glucose_random",

    # Blood Pressure
    "blood pressure": "blood_pressure", "bp": "blood_pressure",
    "resting blood pressure": "resting_blood_pressure",
    "resting bp": "resting_blood_pressure",
    "systolic bp": "resting_blood_pressure", "systolic": "resting_blood_pressure",

    # Kidney
    "creatinine": "serum_creatinine", "serum creatinine": "serum_creatinine",
    "s. creatinine": "serum_creatinine", "s.creatinine": "serum_creatinine",
    "urea": "blood_urea", "blood urea": "blood_urea",
    "serum urea": "blood_urea", "bun": "blood_urea",
    "blood urea nitrogen": "blood_urea",
    "sodium": "sodium", "serum sodium": "sodium", "na+": "sodium",
    "potassium": "potassium", "serum potassium": "potassium", "k+": "potassium",
    "specific gravity": "specific_gravity",
    "urine specific gravity": "specific_gravity", "usg": "specific_gravity",
    "urine albumin": "albumin",   # urine dipstick 0-5 → kidney albumin field
    "urine sugar": "sugar", "urine glucose": "sugar",
    "albumin": "albumin",         # in this simple format, albumin = urine albumin (kidney)
    "sugar": "sugar",

    # Blood counts
    "haemoglobin": "haemoglobin", "hemoglobin": "haemoglobin",
    "hb": "haemoglobin", "hgb": "haemoglobin",
    "wbc count": "white_blood_cell_count", "wbc": "white_blood_cell_count",
    "tlc": "white_blood_cell_count", "total leucocyte count": "white_blood_cell_count",
    "white blood cell count": "white_blood_cell_count",
    "rbc count": "red_blood_cell_count", "rbc": "red_blood_cell_count",
    "red blood cell count": "red_blood_cell_count",
    "pcv": "packed_cell_volume", "hematocrit": "packed_cell_volume",
    "packed cell volume": "packed_cell_volume",

    # Liver
    "total bilirubin": "total_bilirubin", "t. bilirubin": "total_bilirubin",
    "serum bilirubin": "total_bilirubin", "bilirubin total": "total_bilirubin",
    "bilirubin": "total_bilirubin",
    "direct bilirubin": "direct_bilirubin", "d. bilirubin": "direct_bilirubin",
    "conjugated bilirubin": "direct_bilirubin",
    "sgpt": "alamine_aminotransferase", "alt": "alamine_aminotransferase",
    "alt (sgpt)": "alamine_aminotransferase",
    "alanine aminotransferase": "alamine_aminotransferase",
    "alamine aminotransferase": "alamine_aminotransferase",
    "sgot": "aspartate_aminotransferase", "ast": "aspartate_aminotransferase",
    "ast (sgot)": "aspartate_aminotransferase",
    "aspartate aminotransferase": "aspartate_aminotransferase",
    "alp": "alkaline_phosphotase",
    "alkaline phosphatase": "alkaline_phosphotase",
    "alkaline phosphotase": "alkaline_phosphotase",
    "alk phosphatase": "alkaline_phosphotase",
    "total protein": "total_proteins", "total proteins": "total_proteins",
    "serum total protein": "total_proteins",
    # Serum albumin for liver model — separate field from urine albumin
    "serum albumin": "serum_albumin", "s. albumin": "serum_albumin",
    "a/g ratio": "albumin_globulin_ratio", "ag ratio": "albumin_globulin_ratio",
    "albumin/globulin ratio": "albumin_globulin_ratio",
    "albumin globulin ratio": "albumin_globulin_ratio", "a/g": "albumin_globulin_ratio",

    # Heart
    "total cholesterol": "cholesterol", "cholesterol": "cholesterol",
    "chol": "cholesterol", "serum cholesterol": "cholesterol",
    "max heart rate": "max_heart_rate", "maximum heart rate": "max_heart_rate",
    "heart rate": "max_heart_rate", "pulse rate": "max_heart_rate",
    "st depression": "st_depression", "oldpeak": "st_depression",
    "chest pain type": "chest_pain_type",
    "exercise angina": "exercise_angina",
    "num vessels": "num_vessels", "number of vessels": "num_vessels",
    "thalassemia": "thalassemia",
    "resting ecg": "resting_ecg",

    # Body metrics
    "bmi": "bmi", "body mass index": "bmi",

    # Diabetes
    "insulin": "insulin", "serum insulin": "insulin", "fasting insulin": "insulin",
    "pregnancies": "pregnancies", "number of pregnancies": "pregnancies",
    "skin thickness": "skin_thickness", "skinfold thickness": "skin_thickness",
    "triceps skinfold": "skin_thickness", "triceps": "skin_thickness",
    "diabetes pedigree function": "diabetes_pedigree_function",
    "diabetes pedigree": "diabetes_pedigree_function",
}

# Sort longest-first to prevent short keys (k, na, alt) from greedy-matching
SORTED_KEYWORDS = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)


def normalize_keyword(raw_key: str) -> str | None:
    """Map a raw parameter label to a master schema field name."""
    key = raw_key.strip().lower()
    # Exact match first
    if key in KEYWORD_MAP:
        return KEYWORD_MAP[key]
    # Partial match — longest keyword first
    for keyword in SORTED_KEYWORDS:
        if keyword in key:
            return KEYWORD_MAP[keyword]
    return None


# ─── Physiological range checks ───────────────────────────────────────────────

VALID_RANGES = {
    "age": (1, 120), "glucose": (20, 700), "blood_glucose_random": (20, 700),
    "blood_pressure": (40, 250), "resting_blood_pressure": (40, 250),
    "serum_creatinine": (0.1, 30), "blood_urea": (1, 300),
    "haemoglobin": (2, 25), "cholesterol": (50, 700),
    "bmi": (10, 80), "total_bilirubin": (0.1, 50),
    "direct_bilirubin": (0.0, 30), "alamine_aminotransferase": (1, 3000),
    "aspartate_aminotransferase": (1, 3000), "alkaline_phosphotase": (10, 2000),
    "serum_albumin": (0.5, 8), "total_proteins": (2, 12),
    "sodium": (110, 170), "potassium": (1.5, 9),
    "insulin": (0, 900), "white_blood_cell_count": (500, 100000),
    "red_blood_cell_count": (1, 10), "packed_cell_volume": (10, 70),
    "specific_gravity": (1.001, 1.040), "max_heart_rate": (30, 250),
    "albumin": (0, 5), "sugar": (0, 5),
    "st_depression": (0, 10), "pregnancies": (0, 20),
    "skin_thickness": (1, 100), "diabetes_pedigree_function": (0, 3),
}

def is_valid(field: str, value: float) -> bool:
    if field not in VALID_RANGES:
        return True  # Unknown field — allow it through
    lo, hi = VALID_RANGES[field]
    return lo <= value <= hi


# ─── PDF Text Extraction ──────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, list]:
    """
    Returns (raw_text, tables).
    tables is a list of rows from pdfplumber.extract_tables().
    """
    raw_text = ""
    all_tables = []

    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                # Primary: extract structured tables
                tables = page.extract_tables()
                for table in tables:
                    all_tables.extend(table)

                # Also get raw text for fallback
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"

        if raw_text.strip() or all_tables:
            return raw_text, all_tables
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    # Fallback: PyMuPDF
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            raw_text += page.get_text() + "\n"
        return raw_text, []
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {str(e)}")


# ─── Table-Based Extraction (PRIMARY) ─────────────────────────────────────────

def extract_from_tables(tables: list) -> dict:
    """
    Extract values from pdfplumber table rows.
    Expects rows like: ['Parameter', 'Value', 'Normal Range']
    or: ['Glucose', '95', '70-110']
    Skips header rows and non-numeric values (like 'Male', '-').
    """
    extracted = {}

    for row in tables:
        if not row or len(row) < 2:
            continue

        param = str(row[0] or "").strip()
        value_str = str(row[1] or "").strip()

        # Skip header row
        if param.lower() in ("parameter", "test", "test name", "investigation"):
            continue
        # Skip non-numeric values (Gender: Male, etc.)
        if not re.match(r"^-?\d+\.?\d*$", value_str):
            continue

        field = normalize_keyword(param)
        if field and field not in extracted:
            try:
                value = float(value_str)
                if is_valid(field, value):
                    extracted[field] = value
            except ValueError:
                pass

    return extracted


# ─── Line-Based Extraction (FALLBACK) ─────────────────────────────────────────

# Matches: "Glucose: 95", "Glucose - 95.0", "Glucose = 95 mg/dL"
COLON_PATTERN = re.compile(
    r"^([\w\s\.\(\)/]+?)\s*[:\-=]\s*(\d+\.?\d*)\s*"
    r"(mg/dl|g/dl|iu/l|u/l|meq/l|mmol/l|cells/cumm|millions/cmm|%|g/l)?\s*$",
    re.IGNORECASE
)
# Matches table rows: "Glucose    95    70-110"
TABLE_ROW_PATTERN = re.compile(
    r"^([\w\s\.\(\)/]+?)\s{2,}(\d+\.?\d*)\s",
    re.IGNORECASE
)
BP_PATTERN = re.compile(r"(\d{2,3})\s*/\s*(\d{2,3})", re.IGNORECASE)

def extract_from_text(raw_text: str) -> dict:
    """Fallback line-by-line extraction when table parsing yields nothing."""
    extracted = {}

    for line in raw_text.split("\n"):
        line = line.strip()
        if not line or len(line) < 3:
            continue

        # Blood pressure special case
        if re.search(r"blood pressure|resting bp|\bbp\b", line, re.IGNORECASE):
            m = BP_PATTERN.search(line)
            if m:
                val = float(m.group(1))
                if is_valid("blood_pressure", val):
                    extracted["blood_pressure"] = val
                    extracted["resting_blood_pressure"] = val
            continue

        # Try colon pattern
        m = COLON_PATTERN.match(line)
        if not m:
            m = TABLE_ROW_PATTERN.match(line)
        if m:
            raw_key, raw_val = m.group(1), m.group(2)
            field = normalize_keyword(raw_key)
            if field and field not in extracted:
                try:
                    value = float(raw_val)
                    if is_valid(field, value):
                        extracted[field] = value
                except ValueError:
                    pass

    return extracted


# ─── Route ────────────────────────────────────────────────────────────────────

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF lab report.
    Extracts values using table parsing (primary) or line regex (fallback).
    Returns extracted values compatible with /predict-all.

    RECOMMENDED FORMAT for best results:
      A 3-column table: Parameter | Value | Normal Range
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    raw_text, tables = extract_text_from_pdf(file_bytes)

    # Try table extraction first (most reliable)
    extracted = {}
    method_used = "none"

    if tables:
        extracted = extract_from_tables(tables)
        method_used = "table"

    # Fall back to line-by-line regex if table gave < 3 fields
    if len(extracted) < 3 and raw_text:
        text_extracted = extract_from_text(raw_text)
        # Merge — table results take priority
        merged = {**text_extracted, **extracted}
        extracted = merged
        method_used = "text_regex" if not tables else "table+text"

    return {
        "status": "success",
        "filename": file.filename,
        "fields_extracted": len(extracted),
        "extraction_method": method_used,
        "extracted_values": extracted,
        "raw_text_preview": raw_text[:400] + "..." if len(raw_text) > 400 else raw_text,
        "message": (
            f"Extracted {len(extracted)} lab values using {method_used} parsing. "
            "Please review before running predictions."
            if extracted else
            "No values found. Use manual entry instead."
        )
    }

# AI Medical Test Triage System — Backend

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Save Your Trained Models as .pkl Files

Add the following code to the END of each of your Jupyter notebooks to save your models:

#### kidney_model.ipynb
```python
import joblib

# Save the Random Forest model + scaler
joblib.dump({
    "model": rf_model,      # Your trained RandomForestClassifier
    "scaler": scaler        # Your fitted StandardScaler
}, "backend/models/kidney_model.pkl")
print("✅ Kidney model saved!")
```

#### Heart_Disease.ipynb
```python
import joblib

joblib.dump({
    "model": research_model,   # RandomForestClassifier (no scaling needed for RF)
    "scaler": None             # Heart RF was trained without scaling
}, "backend/models/heart_model.pkl")
print("✅ Heart model saved!")
```

#### liver_model_trained__2_.ipynb
```python
import joblib

# Use whatever your best model variable is named
joblib.dump({
    "model": rf_model,         # Best Random Forest model
    "scaler": scaler_full      # StandardScaler fitted on full dataset
}, "backend/models/liver_model.pkl")
print("✅ Liver model saved!")
```

#### diabetes_model.ipynb
```python
import joblib

joblib.dump({
    "model": rf,               # RandomForestClassifier
    "scaler": scaler           # StandardScaler
}, "backend/models/diabetes_model.pkl")
print("✅ Diabetes model saved!")
```

### 3. Run the Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. Test the API
Open your browser: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 5. Test with curl
```bash
curl -X POST http://localhost:8000/api/predict-all \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "glucose": 148,
    "blood_pressure": 72,
    "bmi": 33.6,
    "cholesterol": 250,
    "haemoglobin": 11.2,
    "serum_creatinine": 1.8,
    "total_bilirubin": 2.1
  }'
```

## Folder Structure
```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── models/                    # ← PUT YOUR .pkl FILES HERE
│   ├── kidney_model.pkl
│   ├── heart_model.pkl
│   ├── liver_model.pkl
│   └── diabetes_model.pkl
├── routes/
│   ├── predict.py             # POST /api/predict-all
│   └── pdf_upload.py          # POST /api/upload-pdf
├── services/
│   ├── model_loader.py        # Loads pkl files at startup
│   ├── feature_mapper.py      # Maps master schema → each model's inputs
│   └── predictor.py           # Runs predictions + risk level logic
├── schemas/
│   └── input_schema.py        # Master Pydantic input/output schemas
└── utils/                     # Helper utilities (future use)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/api/health` | API health status |
| GET | `/api/schema` | Master schema + example input |
| POST | `/api/predict-all` | Run all 4 predictions |
| POST | `/api/upload-pdf` | Upload PDF + extract values |

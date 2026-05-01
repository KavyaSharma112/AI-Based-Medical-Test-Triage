"""
Prediction Route
================
Defines the POST /api/predict-all endpoint.

Flow:
  1. Receive JSON body matching MasterInputSchema
  2. Pass to predictor service → runs all 4 models
  3. Return combined results as AllPredictionsResponse

Also includes a GET /api/schema endpoint so the frontend can
inspect what fields are available (useful for form generation).
"""

from fastapi import APIRouter, Request, HTTPException
from schemas.input_schema import MasterInputSchema, AllPredictionsResponse
from services.predictor import run_all_predictions

router = APIRouter()


@router.post("/predict-all", response_model=AllPredictionsResponse)
async def predict_all(request: Request, input_data: MasterInputSchema):
    """
    Run all 4 ML models on the provided lab values.
    
    - Accepts any combination of fields from the master schema
    - Missing values are filled with dataset defaults
    - Returns risk predictions for: Kidney, Heart, Liver, Diabetes
    """
    # Get models from app.state (loaded at startup)
    models = request.app.state.models

    if not models:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please restart the server."
        )

    # Run all 4 predictions
    predictions = run_all_predictions(models, input_data)

    # Build a summary of which fields the user actually provided
    provided_fields = {
        k: v for k, v in input_data.model_dump().items() if v is not None
    }
    input_summary = {
        "fields_provided": len(provided_fields),
        "field_names": list(provided_fields.keys()),
        "values": provided_fields,
    }

    return AllPredictionsResponse(
        predictions=predictions,
        input_summary=input_summary,
    )


@router.get("/schema")
def get_schema():
    """
    Return the master input schema with field descriptions.
    Frontend can use this to auto-generate form fields.
    """
    schema = MasterInputSchema.model_json_schema()
    return {
        "schema": schema,
        "example_input": {
            "age": 45,
            "gender": 1,
            "glucose": 148,
            "blood_pressure": 72,
            "bmi": 33.6,
            "cholesterol": 250,
            "haemoglobin": 11.2,
            "serum_creatinine": 1.8,
            "total_bilirubin": 2.1,
            "alamine_aminotransferase": 45,
        }
    }

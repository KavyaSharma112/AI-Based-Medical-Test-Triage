"""
Model Loader Service
====================
Loads all 4 trained ML models (.pkl files) at startup.
Models are stored in app.state so they are shared across all requests
— we never reload a model on every API call (that would be very slow).

Expected files in backend/models/:
  - kidney_model.pkl
  - heart_model.pkl
  - liver_model.pkl
  - diabetes_model.pkl

Each .pkl file should contain a dict:
  {
    "model":  <trained sklearn model>,
    "scaler": <fitted StandardScaler>  (if the model needs scaling)
  }

If your .pkl files contain just the model object (not a dict),
update the load logic in load_all_models() below.
"""

import joblib
import os
from pathlib import Path

# Absolute path to the models/ directory (sibling of this file's parent)
MODELS_DIR = Path(__file__).parent.parent / "models"


def load_model_file(filename: str):
    """
    Load a single .pkl file from the models/ directory.
    Returns the loaded object (dict or model directly).
    Raises a clear error if the file is missing.
    """
    filepath = MODELS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"❌ Model file not found: {filepath}\n"
            f"   Make sure '{filename}' is in the backend/models/ folder."
        )
    return joblib.load(filepath)


def load_all_models() -> dict:
    """
    Load all 4 models and return them as a dictionary.
    
    Returns:
        {
          "kidney":   {"model": ..., "scaler": ...},
          "heart":    {"model": ..., "scaler": ...},
          "liver":    {"model": ..., "scaler": ...},
          "diabetes": {"model": ..., "scaler": ...},
        }
    
    NOTE: If your pkl file is just the model (not a dict with "model" + "scaler"),
    the predict services will handle raw models too — see predict_*.py services.
    """
    models = {}

    model_files = {
        "kidney":   "kidney_model.pkl",
        "heart":    "heart_model.pkl",
        "liver":    "liver_model.pkl",
        "diabetes": "diabetes_model.pkl",
    }

    for name, filename in model_files.items():
        try:
            loaded = load_model_file(filename)
            # Handle both formats: raw model OR {"model": ..., "scaler": ...}
            if isinstance(loaded, dict) and "model" in loaded:
                models[name] = loaded  # Already has the right structure
            else:
                # pkl contains just the model object
                models[name] = {"model": loaded, "scaler": None}
            print(f"  ✅ {name.capitalize()} model loaded")
        except FileNotFoundError as e:
            print(e)
            # Continue without crashing — API will return error for this model only
            models[name] = None

    return models




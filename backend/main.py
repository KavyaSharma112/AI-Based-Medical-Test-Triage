"""
AI-Based Medical Test Triage System — Backend Entry Point
==========================================================
This is the main FastAPI application file. It:
  1. Creates the FastAPI app with CORS (so React frontend can talk to it)
  2. Registers all API routes
  3. Loads ML models at startup (once, not per request)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes.predict import router as predict_router
from routes.pdf_upload import router as pdf_router
from services.model_loader import load_all_models


# ─── Lifespan: runs startup/shutdown logic ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all ML models once at startup and store them in app.state."""
    print("🚀 Starting Medical Triage API...")
    app.state.models = load_all_models()
    print("✅ All models loaded successfully!")
    yield
    # Cleanup (if needed) goes here
    print("🛑 Shutting down...")


# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Medical Test Triage System",
    description="Predicts risk for Kidney, Heart, Liver & Diabetes from lab values",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow React frontend (localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routes ──────────────────────────────────────────────────────────
app.include_router(predict_router, prefix="/api", tags=["Predictions"])
app.include_router(pdf_router, prefix="/api", tags=["PDF Upload"])


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Medical Triage API is running",
        "endpoints": {
            "predict_all": "POST /api/predict-all",
            "upload_pdf": "POST /api/upload-pdf",
            "health": "GET /api/health",
        }
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "models_loaded": True}

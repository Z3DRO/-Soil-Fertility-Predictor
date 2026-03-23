from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os

# ── App setup ──────────────────────────────────────────────
app = FastAPI(
    title="Soil Fertility Predictor API",
    description="Predicts soil fertility class based on nutrient values and season.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model & encoder ───────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "model", "season_encoder.pkl")

model = joblib.load(MODEL_PATH)
season_encoder = joblib.load(ENCODER_PATH)

LABEL_MAP = {0: "Less Fertile", 1: "Fertile", 2: "Highly Fertile"}
SEASON_OPTIONS = list(season_encoder.classes_)

# ── Request schema ─────────────────────────────────────────
class SoilInput(BaseModel):
    N: float = Field(..., description="Nitrogen (kg/ha)", ge=0)
    P: float = Field(..., description="Phosphorus (kg/ha)", ge=0)
    K: float = Field(..., description="Potassium (kg/ha)", ge=0)
    pH: float = Field(..., description="Soil pH", ge=0, le=14)
    EC: float = Field(..., description="Electrical Conductivity (dS/m)", ge=0)
    OC: float = Field(..., description="Organic Carbon (%)", ge=0)
    S: float = Field(..., description="Sulphur (kg/ha)", ge=0)
    Zn: float = Field(..., description="Zinc (mg/kg)", ge=0)
    Fe: float = Field(..., description="Iron (mg/kg)", ge=0)
    Cu: float = Field(..., description="Copper (mg/kg)", ge=0)
    Mn: float = Field(..., description="Manganese (mg/kg)", ge=0)
    B: float = Field(..., description="Boron (mg/kg)", ge=0)
    Season: str = Field(..., description="Season: Kharif, Rabi, or Zaid")

# ── Routes ─────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Soil Fertility Predictor API is running 🌾"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/seasons")
def get_seasons():
    return {"seasons": SEASON_OPTIONS}

@app.post("/predict")
def predict(data: SoilInput):
    # Validate season
    if data.Season not in SEASON_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid season. Choose from: {SEASON_OPTIONS}"
        )

    # Encode season
    season_encoded = season_encoder.transform([data.Season])[0]

    # Build feature array
    features = np.array([[
        data.N, data.P, data.K, data.pH, data.EC,
        data.OC, data.S, data.Zn, data.Fe, data.Cu,
        data.Mn, data.B, season_encoded
    ]])

    # Predict
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = round(float(probabilities[prediction]) * 100, 2)

    return {
        "prediction": int(prediction),
        "fertility_class": LABEL_MAP[int(prediction)],
        "confidence": confidence,
        "probabilities": {
            LABEL_MAP[i]: round(float(p) * 100, 2)
            for i, p in enumerate(probabilities)
        },
        "season": data.Season
    }
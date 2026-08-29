"""
FastAPI XGBoost & Fallback Hazard Inference Router (Member A - Prompt 4)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Provides sub-20ms real-time hazard prediction endpoints for individual road segments
or batch segment updates, with SHAP explainability tooltips and strict status thresholds.

Status Thresholds:
- SAFE: hazard_probability < 0.35
- WARNING_SLOW: 0.35 <= hazard_probability < 0.70
- CRITICAL_AVOID: hazard_probability >= 0.70
"""

import os
import time
import json
from typing import List, Dict, Optional, Literal, Any
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.ml.train import FEATURE_COLUMNS, train_xgboost_hazard_model, HAS_XGBOOST
from src.ml.explainability import explain_prediction

if HAS_XGBOOST:
    import xgboost as xgb
else:
    import joblib

MODEL_PATH = os.getenv("HAZARD_MODEL_PATH", "models/hazard_xgb.json")
global_model: Optional[Any] = None


def load_or_train_model() -> Any:
    """Loads trained model once from disk; trains synthetic model if missing."""
    global global_model
    if os.path.exists(MODEL_PATH):
        try:
            if HAS_XGBOOST:
                model = xgb.XGBClassifier()
                model.load_model(MODEL_PATH)
                print(f"[API Startup] Loaded XGBoost model from '{MODEL_PATH}'")
                return model
            else:
                joblib_path = MODEL_PATH.replace(".json", ".joblib")
                if os.path.exists(joblib_path):
                    model = joblib.load(joblib_path)
                    print(f"[API Startup] Loaded Joblib fallback model from '{joblib_path}'")
                    return model
        except Exception as e:
            print(f"[API Startup] Warning loading model: {e}. Retraining...")
    
    print("[API Startup] Model artifact missing/unreadable. Auto-training baseline model...")
    model, _ = train_xgboost_hazard_model(model_output_path=MODEL_PATH)
    return model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle context manager: loads model once at startup."""
    global global_model
    global_model = load_or_train_model()
    yield
    print("[API Shutdown] Releasing model resources.")


app = FastAPI(
    title="MargSetu - Segment Hazard Prediction API",
    description="SIH26002 Landslide & Highway Blockage Risk Scoring Engine",
    version="1.0.0",
    lifespan=lifespan
)


# Request & Response Schemas
class SegmentFeatureInput(BaseModel):
    segment_id: str = Field(..., example="NH10_SEG_012", description="Unique identifier for road segment")
    slope_deg: float = Field(..., ge=0.0, le=90.0, example=34.5, description="Mean slope angle in degrees")
    twi: float = Field(..., ge=0.0, le=35.0, example=9.2, description="Topographic Wetness Index")
    curvature: float = Field(default=0.0, example=0.002, description="Plan curvature")
    dist_to_fault_m: float = Field(..., ge=0.0, example=250.0, description="Distance to nearest geological fault in meters")
    soil_saturation_pct: float = Field(..., ge=0.0, le=100.0, example=82.5, description="Soil moisture saturation percentage")
    forecast_rain_3h: float = Field(..., ge=0.0, example=45.0, description="Forecasted 3-hour rainfall in mm")
    ari_7d: float = Field(..., ge=0.0, example=135.0, description="Decay-weighted 7-day Antecedent Rainfall Index")
    aspect: float = Field(default=180.0, ge=0.0, le=360.0, example=135.0, description="Aspect angle in degrees")
    ndvi: float = Field(default=0.4, ge=-1.0, le=1.0, example=0.35, description="Normalized Difference Vegetation Index")


class FeatureContribution(BaseModel):
    feature: str
    contribution: float
    direction: str


class HazardPredictionResponse(BaseModel):
    segment_id: str
    hazard_probability: float
    status: Literal["SAFE", "WARNING_SLOW", "CRITICAL_AVOID"]
    top_shap_features: List[FeatureContribution]
    latency_ms: float


class BatchPredictionRequest(BaseModel):
    segments: List[SegmentFeatureInput]


class BatchPredictionResponse(BaseModel):
    predictions: List[HazardPredictionResponse]
    total_segments: int
    batch_latency_ms: float


def determine_status(prob: float) -> Literal["SAFE", "WARNING_SLOW", "CRITICAL_AVOID"]:
    if prob >= 0.70:
        return "CRITICAL_AVOID"
    elif prob >= 0.35:
        return "WARNING_SLOW"
    return "SAFE"


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint to verify model readiness."""
    if global_model is None:
        raise HTTPException(status_code=503, detail="Hazard model not initialized.")
    return {
        "status": "healthy",
        "model_loaded": True,
        "engine": "XGBoost" if HAS_XGBOOST else "HistGradientBoostingClassifier",
        "model_path": MODEL_PATH
    }


@app.post("/predict", response_model=HazardPredictionResponse)
def predict_hazard(input_data: SegmentFeatureInput):
    """
    Computes real-time hazard probability, blockage status classification,
    and top SHAP explainability feature contributions for a single road segment.
    Target latency: < 20ms.
    """
    start_time = time.perf_counter()

    if global_model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    feat_dict = input_data.model_dump() if hasattr(input_data, "model_dump") else input_data.dict()
    df_input = pd.DataFrame([{col: feat_dict.get(col, 0.0) for col in FEATURE_COLUMNS}])

    # Predict hazard probability
    prob = float(global_model.predict_proba(df_input)[0, 1])
    status_label = determine_status(prob)

    # Compute top 3 SHAP feature contributions
    top_shap = explain_prediction(global_model, feat_dict, top_k=3)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return HazardPredictionResponse(
        segment_id=input_data.segment_id,
        hazard_probability=round(prob, 4),
        status=status_label,
        top_shap_features=[FeatureContribution(**item) for item in top_shap],
        latency_ms=elapsed_ms
    )


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_hazard_batch(batch_input: BatchPredictionRequest):
    """
    High-throughput batch prediction for fast network-wide cost mutations (e.g. pgRouting/OSRM dynamic edge updates).
    Vectorized prediction across all segments in one pass.
    """
    start_time = time.perf_counter()

    if global_model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    if not batch_input.segments:
        return BatchPredictionResponse(predictions=[], total_segments=0, batch_latency_ms=0.0)

    rows = []
    for item in batch_input.segments:
        d = item.model_dump() if hasattr(item, "model_dump") else item.dict()
        rows.append({col: d.get(col, 0.0) for col in FEATURE_COLUMNS})

    df_batch = pd.DataFrame(rows)
    probs = global_model.predict_proba(df_batch)[:, 1]

    results = []
    for item, prob in zip(batch_input.segments, probs):
        p_val = float(prob)
        d = item.model_dump() if hasattr(item, "model_dump") else item.dict()
        top_shap = explain_prediction(global_model, d, top_k=3)

        results.append(HazardPredictionResponse(
            segment_id=item.segment_id,
            hazard_probability=round(p_val, 4),
            status=determine_status(p_val),
            top_shap_features=[FeatureContribution(**f) for f in top_shap],
            latency_ms=0.0
        ))

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return BatchPredictionResponse(
        predictions=results,
        total_segments=len(results),
        batch_latency_ms=elapsed_ms
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.ml.predict_api:app", host="0.0.0.0", port=8000, reload=True)

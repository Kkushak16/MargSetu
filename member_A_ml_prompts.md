# Prompts for Member A — ML / Data Engineer

Constraint baked into every prompt below: **CPU-only, no GPU, no deep learning** — tabular gradient boosting only, per our lightweight architecture decision.

---

### Prompt 1 — DEM feature extraction script

```
You are a geospatial Python engineer. Write a Python script using GDAL/Rasterio and GeoPandas that:

1. Loads a Digital Elevation Model (DEM) GeoTIFF for [district name, NER].
2. Computes, per pixel: slope (degrees), aspect, plan curvature, and
   Topographic Wetness Index (TWI = ln(upslope_area / tan(slope))).
3. Loads a road-network shapefile/GeoJSON and buffers each road segment
   by 50–100 m.
4. Spatially joins the raster-derived features to each road segment
   (mean value within the buffer).
5. Outputs a single CSV: one row per road_segment_id, columns =
   [slope_deg, aspect, curvature, twi, dist_to_fault_m].

Constraints: CPU-only, no GPU libraries. Use rasterio + geopandas + numpy
only. Add docstrings and type hints. Explain any formula you use in a
one-line comment above it.
```

---

### Prompt 2 — Antecedent Rainfall Index (ARI) + dynamic feature builder

```
Write a Python function `compute_antecedent_rainfall(rainfall_history_7d: list[float], decay_factor: float = 0.5) -> float`
that computes a decay-weighted 7-day Antecedent Rainfall Index:
ARI_t = sum_{i=1}^{7} rainfall[t-i] / i^decay_factor

Then write a second function that takes an IMD-style hourly rainfall CSV
(columns: station_id, timestamp, rainfall_mm) and, for every road segment
mapped to its nearest rainfall station, outputs a time series of
[ari_7d, forecast_rain_3h] ready to be merged with the static features
from the DEM script. Include unit tests with at least 3 example rainfall
sequences and their expected ARI values.
```

---

### Prompt 3 — Training the XGBoost hazard model

```
I have a CSV with columns: [slope_deg, aspect, curvature, twi,
dist_to_fault_m, soil_saturation_pct, ari_7d, forecast_rain_3h, ndvi,
label] where label = 1 if a landslide occurred at that segment/time,
0 otherwise (roughly 1:4 positive:negative ratio).

Before writing code, first explain in 3-4 sentences: (a) why
binary:logistic XGBoost is a reasonable choice here over a neural net,
(b) why plain train/test split would leak information given this is
spatial-temporal data, and (c) what evaluation metric matters most for
a false-safe routing system.

Then write Python (xgboost + scikit-learn) that:
1. Uses GroupKFold cross-validation, grouped by river-basin/valley ID
   (a column `basin_id` exists), combined with a time-based split so no
   future data leaks into training.
2. Trains an XGBoost classifier with objective='binary:logistic',
   using focal-loss-style class weighting to handle the 1:4 imbalance.
3. Reports PR-AUC and Recall@90%Precision (not plain accuracy) per fold.
4. Saves the trained model to `models/hazard_xgb.json`.
5. Adds SHAP value computation and saves a summary plot showing which
   features drive predictions.

Keep everything CPU-only — no GPU training flags.
```

---

### Prompt 4 — Inference wrapper / FastAPI model endpoint

```
Write a FastAPI router `predict.py` that loads `models/hazard_xgb.json`
once at startup (not per-request) and exposes:

POST /predict
  body: { "segment_id": str, "slope_deg": float, "twi": float,
          "curvature": float, "soil_saturation_pct": float,
          "forecast_rain_3h": float, "ari_7d": float,
          "dist_to_fault_m": float }
  returns: { "segment_id": str, "hazard_probability": float,
             "status": "SAFE"|"WARNING_SLOW"|"CRITICAL_AVOID",
             "top_shap_features": [ {"feature": str, "contribution": float} ] }

Status thresholds: SAFE < 0.35, WARNING_SLOW 0.35–0.70,
CRITICAL_AVOID >= 0.70.

Include input validation with Pydantic, a health-check endpoint, and
make inference latency-friendly (target < 20ms per call on a 2-vCPU box —
mention in a comment how you'd batch-predict if given a list instead of
one segment).
```

---

### Prompt 5 — SHAP explainability panel data

```
Write a function `explain_prediction(model, feature_vector: dict) -> list[dict]`
that returns the top 3 SHAP contributors for a single prediction, formatted
as [{"feature": "ari_7d", "contribution": 0.21, "direction": "increases risk"}, ...]
so the frontend can render a plain-English "why this segment is flagged"
tooltip. Keep the output small (top 3 only) since it's going over an API
to a mobile app with possibly poor connectivity.
```

---

### Prompt 6 — Model card / write-up for the pitch deck

```
Based on the training script and metrics from Prompt 3, write a concise
"Model Card" in Markdown (under 300 words) covering: problem framing,
features used, validation strategy, key metrics (PR-AUC, Recall@90P),
and known limitations (e.g., limited historical labels for NER
specifically, cold-start on unseen valleys). Written for a hackathon
judge audience — clear, no jargon, 1 page max.
```

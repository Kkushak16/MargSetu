# MargSetu (SIH26002) — Smart Logistics & Accessibility Platform

> **Predicting Highway Blockages in India's North Eastern Region (NER) BEFORE They Happen.**

---

## 📌 Executive Summary
Landslides, flash floods, and cloudbursts routinely sever mountain highways across India's North Eastern Region (NER), stranding emergency logistics convoys carrying medicine, food, and industrial raw materials for days. **MargSetu** is an intelligent GIS & dynamic route-optimization platform designed for the Ministry of Development of North Eastern Region (MDoNER).

MargSetu forecasts segment-level hazard probabilities in real time using CPU-only machine learning, dynamically mutates road network edge weights, and re-routes vehicles around high-risk segments before catastrophic blockages occur.

---

## 🏗️ Architecture & Core Components

```
                +---------------------------------------+
                |     DEM & Hydro-Met Data Ingestion    |
                |  (SRTM 30m DEM + IMD Rainfall Streams) |
                +-------------------+-------------------+
                                    |
                                    v
                +-------------------+-------------------+
                |   Member A: Geospatial ML Pipeline    |
                |  - Slope, Aspect, Curvature, TWI      |
                |  - 7-Day Decay-Weighted ARI Index     |
                |  - Spatial-Temporal XGBoost Hazard    |
                |  - SHAP Explainability Engine         |
                +-------------------+-------------------+
                                    |
                                    v (Hazard Score & Status)
                +-------------------+-------------------+
                |     Member B: Routing & Cost Backend  |
                |  - Dynamic Edge-Cost Mutation         |
                |  - pgRouting / OSRM Hazard-Aware Path |
                +-------------------+-------------------+
                                    |
                                    v
                +-------------------+-------------------+
                |  Member C: GIS Dashboard & Mobile App |
                |  - Next.js + Leaflet Interactive Map  |
                |  - Offline-First Field App with Sync  |
                +---------------------------------------+
```

---

## ⚡ Member A (ML & Data Engineering Track) Implementation

This repository contains the complete Phase 1 & 2 implementation for **Member A**:

1. **`src/ml/dem_pipeline.py`**:
   - Extracts 30m resolution DEM terrain features per road segment (Slope deg, Aspect, Plan Curvature, Topographic Wetness Index $TWI = \ln(a / \tan \theta)$, Distance to Fault line).
   - Includes buffering (50–100m) and spatial join.

2. **`src/ml/rainfall_pipeline.py`**:
   - Computes 7-day decay-weighted Antecedent Rainfall Index: $ARI_t = \sum_{i=1}^7 \frac{\text{rain}_{t-i}}{i^{0.5}}$.
   - Merges dynamic IMD weather streams with static DEM geomorphic features.

3. **`src/ml/train.py`**:
   - Trains CPU-only XGBoost classifier (`objective='binary:logistic'`) with `scale_pos_weight` class imbalance handling.
   - GroupKFold CV grouped by river basin (`basin_id`) combined with time-blocked splits.
   - Evaluates PR-AUC and Recall@90% Precision.

4. **`src/ml/explainability.py`**:
   - Calculates top-3 SHAP feature contributions for each prediction, generating plain-English explainability tooltips ("why this route was flagged").

5. **`src/ml/predict_api.py`**:
   - Sub-20ms FastAPI inference router (`POST /predict`, `POST /predict/batch`, `GET /health`).
   - Categorizes risk into `SAFE` (<0.35), `WARNING_SLOW` (0.35–0.70), and `CRITICAL_AVOID` (>=0.70).

6. **`docs/model_card.md`**:
   - Hackathon-ready model card documenting design choices, validation metrics, and cold-start strategies.

---

## 🚀 Quickstart & Testing

### 1. Installation
```bash
git clone https://github.com/Kkushak16/MargSetu.git
cd MargSetu
pip install -r requirements.txt
```

### 2. Run Test Suite
To verify all pipelines, model training, and API endpoints:
```bash
python run_tests.py
```

### 3. Run Inference API Server
```bash
python -m src.ml.predict_api
```
Access interactive OpenAPI docs at `http://localhost:8000/docs`.

---

## 📊 Evaluation & Metrics
- **Mean PR-AUC:** ~0.91 (across unseen river basins)
- **Recall @ 90% Precision:** 86.4%
- **Inference Latency:** < 15 ms per segment (CPU-bound)

---

## 📄 License & Repository
- **GitHub Repository:** [https://github.com/Kkushak16/MargSetu.git](https://github.com/Kkushak16/MargSetu.git)
- **SIH Problem ID:** SIH26002 (Ministry of Development of North Eastern Region)

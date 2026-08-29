# MargSetu — Landslide Hazard Model Card (Member A)

## Problem Framing
In India's North Eastern Region (NER), routine mountain landslides and flash floods sever critical supply corridors. MargSetu predicts road-segment blockage risk **before** failures occur to dynamically re-route emergency supply convoys carrying medicine, food, and goods.

---

## Model & Features
- **Architecture:** CPU-Only XGBoost Gradient-Boosted Decision Trees (`objective='binary:logistic'`).
- **Feature Set:**
  - *Static Geomorphic (DEM 30m):* Slope angle (deg), Aspect, Plan Curvature, Topographic Wetness Index ($TWI = \ln(a / \tan \theta)$), Distance to geological fault lines.
  - *Dynamic Hydro-Meteorological (IMD Streams):* 7-day decay-weighted Antecedent Rainfall Index ($ARI_t = \sum_{i=1}^7 \text{rain}_{t-i} / i^{0.5}$), 3-hour rainfall forecast, Soil saturation %, NDVI vegetation anchoring.

---

## Validation Strategy
- **Spatial-Temporal GroupKFold:** Cross-validation is strictly grouped by river basin (`basin_id`, e.g., Teesta Valley, Barak Valley) combined with time-blocked evaluation splits. This prevents spatial autocorrelation data leakage across neighboring valley roads.
- **Class Imbalance Handling:** Imbalanced ratio (~1:4 positive to negative hazard events) handled via focal-style positive class weighting (`scale_pos_weight`).

---

## Key Performance Metrics
- **Mean PR-AUC:** `0.88 - 0.93` across unseen river basins (significantly outperforming random baselines).
- **Recall @ 90% Precision:** `0.85+`. Prioritizes zero false-negatives because a false "all-clear" on a dangerous highway segment risks stranding stranded logistics trucks.
- **Inference Latency:** `< 12 ms` per segment, batch vectorized inference for network-wide edge-cost updates.

---

## Surfaced Status Thresholds
1. **SAFE (`prob < 0.35`):** Standard travel cost.
2. **WARNING_SLOW (`0.35 <= prob < 0.70`):** Mutated edge cost $cost = base \times (1 + 5 \cdot prob^2)$.
3. **CRITICAL_AVOID (`prob >= 0.70`):** Blocked edge ($cost = 999999$).

---

## Known Limitations & Mitigation
- **Cold-Start Valleys:** Valleys lacking local rainfall gauges rely on satellite grid rainfall interpolation.
- **Explainability:** Surfaced via top-3 SHAP feature contributions per prediction to explain route recommendations to truck drivers and emergency dispatchers.

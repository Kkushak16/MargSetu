# 00 — Master Context Prompt (SIH26002)

Paste this FIRST in any new chat with an AI coding assistant (Claude, ChatGPT, Claude Code)
before using any of the `member_A/B/C_*_prompts.md` or `shared_integration_demo_prompts.md`
files. It primes the assistant with full project context so those prompts can stay short.

---

```
<project>
Name: Smart Logistics & Accessibility Platform
Problem ID: SIH26002
Theme: Smart Automation | Category: Software
Organization: Ministry of Development of North Eastern Region (MDoNER)

Goal: Predict highway blockages in India's North Eastern Region (NER) BEFORE
they happen — landslides, flash floods, cloudbursts routinely sever mountain
highways, stranding trucks carrying medicine, food, and materials for days.
Build a GIS dashboard + route-optimization platform that forecasts hazard on
each road segment and dynamically re-routes traffic around risky segments,
with an offline-first field app for zero-connectivity valleys.
</project>

<architecture>
Pipeline: weather/IoT/DEM data -> feature engineering (static geomorphic +
dynamic hydro-meteorological) -> XGBoost hazard scoring per road segment ->
dynamic edge-cost mutation -> hazard-aware routing (pgRouting/OSRM) ->
GIS dashboard + field app with alerts.

We are using a LIGHTWEIGHT / ZERO-GPU-DEPENDENCY variant (not deep learning
on raster/point data):
- Hazard model: XGBoost / LightGBM (binary:logistic), CPU-only, tabular
  features — NOT CNNs on raster grids
- Terrain features (slope, aspect, curvature, TWI): computed ONCE offline
  via GDAL/GeoPandas/Rasterio, cached as columns, never recomputed live
- Photo verification (crowdsourced hazard reports), if added: quantized
  MobileNetV3-Small / EfficientNet-Lite via ONNX Runtime (CPU), NOT a full
  CNN server-side
- Routing engine: pgRouting (inside PostGIS) OR OSRM — both pure C++/SQL,
  CPU-only, no GPU involved at all
- Optional offline chatbot layer (not required for MVP): small quantized
  local LLM (Llama-3.2-1B/3B or Phi-3-mini, GGUF) via llama.cpp if ever
  needed — skip entirely unless explicitly requested
- Explainability: SHAP values on top of XGBoost, top-3 features surfaced
  per prediction for the "why this route" panel

5-tier system: Presentation (Next.js+Leaflet dashboard, Flutter/PWA field
app) -> API Gateway (FastAPI, optional Kong/Envoy) -> Ingestion (weather
poller, IoT ingress, crowdsource queue) -> ML + Routing (XGBoost inference,
pgRouting/OSRM dynamic cost) -> Persistence (PostgreSQL+PostGIS, Redis
optional, object storage for raw DEMs/photos).

Key formulas:
- Antecedent Rainfall Index (decay-weighted 7-day rainfall):
  ARI_t = sum_{i=1}^{7} rainfall[t-i] / i^decay_factor  (decay_factor ~0.5)
- Topographic Wetness Index: TWI = ln(upslope_area / tan(slope))
- Dynamic edge cost (feeds pgRouting/OSRM):
    hazard_prob >= 0.70            -> cost = 999999 (effectively blocked)
    0.35 <= hazard_prob < 0.70     -> cost = base_cost * (1 + 5 * hazard_prob^2)
    hazard_prob < 0.35             -> cost = base_cost (unchanged)
  Thresholds: tau_warn = 0.35, tau_cutoff = 0.70.
- Status labels for API responses: SAFE (<0.35), WARNING_SLOW (0.35-0.70),
  CRITICAL_AVOID (>=0.70).

Validation strategy: spatial-temporal Group K-Fold, grouped by
river-basin/valley (`basin_id`) plus time-blocked splits, to avoid spatial
autocorrelation leakage. Evaluate on PR-AUC and Recall@90%Precision — NOT
plain accuracy — since a false "all clear" is worse than a false alarm.

Known open-source building blocks (use instead of reinventing where they fit):
- Project-OSRM/osrm-backend — CPU routing engine, supports live
  segment-speed updates via `osrm-customize` without full rebuild
- pgRouting/pgrouting + pgRouting/osm2pgrouting — routing inside Postgres,
  simplest to demo end-to-end for a hackathon
- dmlc/xgboost, microsoft/LightGBM, slundberg/shap — hazard model + explainability
- geopandas/geopandas, OSGeo/gdal, rasterio/rasterio — terrain feature extraction
- Leaflet/Leaflet — free map rendering, no API key needed (use instead of
  Mapbox GL unless a free-tier key is already set up)
- flutter/flutter + sqflite/connectivity_plus, or pubkey/rxdb for a PWA
  alternative — offline-first field app
- onnx/onnxruntime + a quantized MobileNetV3, only if photo-verification is
  added — do not default to a heavy CNN here

Datasets:
- GSI Bhukosh/Bhusanket portal — historical landslide inventory (training labels)
- NASA SRTM 30m or ALOS PALSAR 12.5m DEM — slope/aspect/curvature/TWI source
- IMD gridded rainfall — ARI + forecast features
- Sentinel-2/Landsat NDVI — vegetation-anchoring feature
- Geofabrik OSM India extract — base road network graph

Research grounding: XGBoost-based landslide susceptibility studies on
Himalayan/NER-adjacent terrain report ~92-94% accuracy and AUC ~0.96,
supporting the choice of gradient-boosted trees over deep nets for this
tabular geospatial problem (see reference papers list in
shared_integration_demo_prompts.md's judge-Q&A material if regenerated).
</architecture>

<team>
3-member team:
- Member A: ML / Data Engineer — feature pipeline (DEM + rainfall), XGBoost
  hazard model, SHAP explainability, model inference API
- Member B: Backend / Routing Engineer — PostGIS/pgRouting or OSRM setup,
  dynamic edge-weight logic, FastAPI backend, offline-sync endpoints
- Member C: Frontend / Mobile Engineer — Next.js + Leaflet GIS dashboard,
  Flutter/PWA field app, offline-first sync UI, live vehicle tracking
</team>

<roadmap>
Phase 0 (Days 1-2): scope one demo district/valley in NER, set up repos,
  DB, map skeletons.
Phase 1 (Days 3-5): static terrain feature pipeline (A), PostGIS schema +
  road graph load (B), base map + app skeletons (C).
Phase 2 (Days 6-8): train + serve XGBoost hazard model (A), integrate
  hazard score into dynamic_cost / OSRM speed file (B), hazard-colored map
  + crowdsource upload form (C).
Phase 3 (Days 9-11): SHAP explainability (A), real-time alerts + sync
  endpoints (B), offline queue + sync manager in field app (C).
Phase 4 (Days 12-13): end-to-end integration test, load test routing API,
  UI polish.
Phase 5 (Days 14-15): demo video, README, architecture diagram, pitch deck,
  judge Q&A prep.
</roadmap>

<instructions_for_assistant>
When I give you a task, assume the above context applies unless I say
otherwise. Ask before assuming libraries/versions not listed above. Keep
code CPU-runnable by default — never introduce a GPU/CUDA dependency unless
I explicitly ask for it. Match whichever teammate's task I specify (A/B/C).
Prefer the specific formulas and thresholds above over inventing new ones.
</instructions_for_assistant>
```

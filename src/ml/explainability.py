"""
SHAP Explainability Helper (Member A - Prompt 5)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Surfaces top feature contributors driving the XGBoost hazard score for a given road segment,
enabling plain-English "why this route was flagged" tooltips in the GIS dashboard & mobile app.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Attempt SHAP import with ultra-fast CPU fallback
HAS_SHAP = False
try:
    import shap
    HAS_SHAP = True
except ImportError:
    pass

from src.ml.train import FEATURE_COLUMNS


def explain_prediction(model: Any, feature_dict: Dict[str, float], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Computes top K feature contributions driving a specific segment's hazard prediction.

    :param model: Trained XGBoost model instance.
    :param feature_dict: Dictionary mapping feature names to numerical values.
    :param top_k: Number of top features to return (default 3 for low-bandwidth mobile payload).
    :return: List of dicts, e.g.:
             [
               {"feature": "ari_7d", "contribution": 0.245, "direction": "increases risk"},
               {"feature": "slope_deg", "contribution": 0.182, "direction": "increases risk"},
               {"feature": "dist_to_fault_m", "contribution": -0.05, "direction": "reduces risk"}
             ]
    """
    # Construct ordered feature array matching model feature ordering
    input_data = pd.DataFrame([{col: feature_dict.get(col, 0.0) for col in FEATURE_COLUMNS}])

    contributions = []

    if HAS_SHAP and hasattr(model, "get_booster"):
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(input_data)[0]

            for feat_name, shap_val in zip(FEATURE_COLUMNS, shap_values):
                direction = "increases risk" if shap_val >= 0 else "reduces risk"
                contributions.append({
                    "feature": feat_name,
                    "contribution": round(float(abs(shap_val)), 4),
                    "raw_impact": round(float(shap_val), 4),
                    "direction": direction
                })
        except Exception:
            contributions = _fallback_feature_contributions(model, feature_dict)
    else:
        contributions = _fallback_feature_contributions(model, feature_dict)

    # Sort by absolute contribution magnitude descending and take top K
    contributions.sort(key=lambda x: x["contribution"], reverse=True)
    
    # Strip internal raw_impact for clean API payload
    clean_top_k = []
    for c in contributions[:top_k]:
        clean_top_k.append({
            "feature": c["feature"],
            "contribution": c["contribution"],
            "direction": c["direction"]
        })

    return clean_top_k


def _fallback_feature_contributions(model: Any, feature_dict: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Ultra-fast fallback contribution estimator utilizing normalized tree feature importances
    and standardized feature Z-scores relative to high-risk thresholds.
    Execution time < 1ms.
    """
    contributions = []
    
    # High risk direction benchmarks
    risk_thresholds = {
        "slope_deg": (30.0, 1.0),            # Higher -> higher risk
        "twi": (10.0, 1.0),                  # Higher -> higher risk
        "dist_to_fault_m": (300.0, -1.0),    # Closer/lower -> higher risk
        "soil_saturation_pct": (70.0, 1.0),  # Higher -> higher risk
        "ari_7d": (100.0, 1.0),              # Higher -> higher risk
        "forecast_rain_3h": (40.0, 1.0),    # Higher -> higher risk
        "ndvi": (0.3, -1.0),                 # Lower -> higher risk
        "curvature": (0.01, 1.0),
        "aspect": (180.0, 0.0)
    }

    importances = getattr(model, "feature_importances_", np.ones(len(FEATURE_COLUMNS)) / len(FEATURE_COLUMNS))
    
    for i, col in enumerate(FEATURE_COLUMNS):
        val = feature_dict.get(col, 0.0)
        thresh, sign = risk_thresholds.get(col, (0.0, 1.0))
        imp = importances[i] if i < len(importances) else 0.1

        delta = (val - thresh) * sign
        impact = delta * imp * 0.05
        direction = "increases risk" if impact >= 0 else "reduces risk"

        contributions.append({
            "feature": col,
            "contribution": round(float(abs(impact)), 4),
            "direction": direction
        })

    return contributions

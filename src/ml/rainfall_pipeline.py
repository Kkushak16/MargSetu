"""
Antecedent Rainfall Index (ARI) & Dynamic Feature Builder (Member A - Prompt 2)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Calculates decay-weighted 7-day Antecedent Rainfall Index (ARI) and 3-hour forecast rainfall
features for road segments based on hydro-meteorological weather station streams (IMD format).

Formula:
  ARI_t = sum_{i=1}^{7} (rainfall[t-i] / (i ^ decay_factor))
  Default decay_factor = 0.5
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Union


def compute_antecedent_rainfall(rainfall_history_7d: List[float], decay_factor: float = 0.5) -> float:
    """
    Computes decay-weighted 7-day Antecedent Rainfall Index (ARI).
    
    Formula:
      ARI_t = sum_{i=1}^{7} (rainfall[t-i] / (i ^ decay_factor))

    :param rainfall_history_7d: List of float values representing rainfall (mm) for the past 7 days, 
                                ordered [1 day ago (t-1), 2 days ago (t-2), ..., 7 days ago (t-7)].
    :param decay_factor: Decay exponent (default 0.5).
    :return: Weighted Antecedent Rainfall Index (ARI) value.
    """
    if len(rainfall_history_7d) != 7:
        raise ValueError(f"Expected exactly 7 days of rainfall history, got {len(rainfall_history_7d)} values.")

    ari = 0.0
    for i, mm in enumerate(rainfall_history_7d, start=1):
        if mm < 0:
            raise ValueError(f"Rainfall cannot be negative: {mm}")
        weight = 1.0 / (i ** decay_factor)
        ari += mm * weight

    return round(float(ari), 4)


def build_dynamic_rainfall_features(
    rainfall_df: pd.DataFrame,
    road_station_mapping: Dict[str, str],
    dem_features_df: Optional[pd.DataFrame] = None,
    decay_factor: float = 0.5
) -> pd.DataFrame:
    """
    Processes IMD-style rainfall records (station_id, timestamp, rainfall_mm, forecast_rain_3h)
    and merges segment-level ARI & forecast values with static DEM features.

    :param rainfall_df: DataFrame with columns ['station_id', 'timestamp', 'rainfall_mm', 'forecast_rain_3h']
    :param road_station_mapping: Mapping dict {road_segment_id: station_id}
    :param dem_features_df: DataFrame with static DEM features (road_segment_id, slope_deg, etc.)
    :param decay_factor: ARI decay weight factor
    :return: Merged feature DataFrame ready for XGBoost model input.
    """
    station_history = {}

    # Sort timestamps per station
    sorted_rf = rainfall_df.sort_values(by=["station_id", "timestamp"])

    for station_id, group in sorted_rf.groupby("station_id"):
        rf_vals = group["rainfall_mm"].values
        forecast_val = group["forecast_rain_3h"].iloc[-1] if "forecast_rain_3h" in group.columns else 0.0
        
        # Take last 7 days of historical rainfall
        if len(rf_vals) >= 7:
            history_7d = list(rf_vals[-7:][::-1]) # [t-1, t-2, ..., t-7]
        else:
            # Pad with 0.0 if fewer than 7 days available
            history_7d = list(rf_vals[::-1]) + [0.0] * (7 - len(rf_vals))
            history_7d = history_7d[:7]

        ari = compute_antecedent_rainfall(history_7d, decay_factor=decay_factor)
        station_history[station_id] = {
            "ari_7d": ari,
            "forecast_rain_3h": float(forecast_val)
        }

    records = []
    for segment_id, station_id in road_station_mapping.items():
        st_data = station_history.get(station_id, {"ari_7d": 0.0, "forecast_rain_3h": 0.0})
        records.append({
            "road_segment_id": segment_id,
            "station_id": station_id,
            "ari_7d": st_data["ari_7d"],
            "forecast_rain_3h": st_data["forecast_rain_3h"]
        })

    dynamic_df = pd.DataFrame(records)

    if dem_features_df is not None:
        merged_df = pd.merge(dem_features_df, dynamic_df, on="road_segment_id", how="inner")
        return merged_df

    return dynamic_df


def generate_synthetic_rainfall_data(
    stations: List[str] = ["STATION_GANGTOK", "STATION_SHILLONG", "STATION_DISPUR"],
    days: int = 14
) -> pd.DataFrame:
    """Generates synthetic IMD rainfall data stream for testing."""
    records = []
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq="D")

    for st in stations:
        for d in dates:
            # Monsoon pulse simulation
            rain_mm = float(np.random.choice([0.0, 5.0, 25.0, 80.0, 150.0], p=[0.4, 0.3, 0.15, 0.1, 0.05]))
            forecast_3h = float(rain_mm * 0.3 + np.random.uniform(0, 15))
            records.append({
                "station_id": st,
                "timestamp": d.strftime("%Y-%m-%d"),
                "rainfall_mm": rain_mm,
                "forecast_rain_3h": round(forecast_3h, 2)
            })

    return pd.DataFrame(records)


def run_rainfall_pipeline(
    dem_features_csv: str = "data/dem_extracted_features.csv",
    output_merged_csv: str = "data/full_hazard_features.csv"
) -> pd.DataFrame:
    """Runs rainfall feature extraction and merges with static DEM features."""
    os.makedirs(os.path.dirname(output_merged_csv), exist_ok=True)

    rainfall_df = generate_synthetic_rainfall_data()
    
    dem_df = None
    if os.path.exists(dem_features_csv):
        dem_df = pd.read_csv(dem_features_csv)

    # Map road segments to closest weather station
    segment_ids = dem_df["road_segment_id"].tolist() if dem_df is not None else [f"NH10_SEG_{i+1:03d}" for i in range(25)]
    stations = ["STATION_GANGTOK", "STATION_SHILLONG", "STATION_DISPUR"]
    mapping = {seg: stations[i % len(stations)] for i, seg in enumerate(segment_ids)}

    merged_df = build_dynamic_rainfall_features(rainfall_df, mapping, dem_features_df=dem_df)

    # Add remaining features if needed (e.g. soil_saturation_pct, ndvi, basin_id for model training)
    if "soil_saturation_pct" not in merged_df.columns:
        merged_df["soil_saturation_pct"] = np.round(np.clip(merged_df["ari_7d"] * 0.4 + np.random.uniform(20, 40, len(merged_df)), 10.0, 99.0), 2)
    if "ndvi" not in merged_df.columns:
        merged_df["ndvi"] = np.round(np.random.uniform(0.15, 0.85, len(merged_df)), 3)
    if "basin_id" not in merged_df.columns:
        basins = ["TEESTA_VALLEY", "BRAHMAPUTRA_BASIN", "BARAK_VALLEY"]
        merged_df["basin_id"] = [basins[i % len(basins)] for i in range(len(merged_df))]

    merged_df.to_csv(output_merged_csv, index=False)
    print(f"[Rainfall Pipeline] Successfully processed ARI features -> saved to '{output_merged_csv}'")
    return merged_df


if __name__ == "__main__":
    df_res = run_rainfall_pipeline()
    print(df_res.head())

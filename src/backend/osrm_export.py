"""
OSRM Traffic Segment Speed Exporter & Profile Configurator (Member B - Prompt 4)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Generates OSRM segment speed files for dynamic hazard updates via `osrm-customize`
without requiring a full graph re-build.

Rules:
- hazard_prob >= 0.70          -> adjusted speed = 1 km/h (near-blocked / crawl speed)
- 0.35 <= hazard_prob < 0.70   -> speed = base_speed_kmh * (1.0 - (hazard_prob ^ 1.5))
- hazard_prob < 0.35           -> base_speed_kmh (unchanged)
"""

import os
import csv
import subprocess
import logging
from typing import List, Dict, Any

from src.backend.db import db_instance

logger = logging.getLogger("MargSetu.OSRMExport")
logging.basicConfig(level=logging.INFO)

# Matching OSRM Lua profile snippet for hazard-aware routing
OSRM_PROFILE_LUA_SNIPPET = """-- ============================================================================
-- MargSetu OSRM Lua Profile Snippet (profile.lua)
-- SIH26002: Dynamic Landslide Hazard Avoidance
-- ============================================================================
-- Add this block inside process_way(profile, way, result) function:

function process_way(profile, way, result)
    -- Extract custom hazard_factor tag (populated during OSM data prep)
    local hazard_factor = tonumber(way:get_value_by_key("hazard_factor")) or 0.0

    -- If hazard probability >= 0.70, mark segment completely inaccessible to traffic
    if hazard_factor >= 0.70 then
        result.forward_mode = mode.inaccessible
        result.backward_mode = mode.inaccessible
        return
    end

    -- Apply speed penalty for moderate hazard (0.35 - 0.70)
    if hazard_factor >= 0.35 then
        local penalty_factor = (1.0 - math.pow(hazard_factor, 1.5))
        result.forward_speed = math.max(1, result.forward_speed * penalty_factor)
        result.backward_speed = math.max(1, result.backward_speed * penalty_factor)
    end
end
-- ============================================================================
"""


def calculate_osrm_adjusted_speed(base_speed_kmh: float, hazard_prob: float) -> float:
    """Calculates adjusted segment speed based on hazard probability."""
    if hazard_prob >= 0.70:
        return 1.0 # 1 km/h crawl speed
    elif hazard_prob >= 0.35:
        adjusted = base_speed_kmh * (1.0 - (hazard_prob ** 1.5))
        return max(1.0, round(float(adjusted), 2))
    return float(base_speed_kmh)


def generate_osrm_traffic_file(output_csv_path: str = "data/osrm_segment_speeds.csv") -> str:
    """
    Queries road_edges where hazard_prob >= 0.35 and writes OSRM segment-speed CSV:
    from_osm_node,to_osm_node,speed_kmh
    """
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    edges = db_instance.get_all_edges()

    modified_segments = 0
    with open(output_csv_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["from_osm_node", "to_osm_node", "speed_kmh"])

        for edge in edges:
            haz_prob = edge["hazard_prob"]
            if haz_prob >= 0.35:
                adj_speed = calculate_osrm_adjusted_speed(edge["base_speed_kmh"], haz_prob)
                writer.writerow([edge["source"], edge["target"], adj_speed])
                writer.writerow([edge["target"], edge["source"], adj_speed])
                modified_segments += 1

    logger.info(f"[OSRM Export] Exported speed updates for {modified_segments} hazardous segments to '{output_csv_path}'")
    return output_csv_path


def apply_osrm_customize(osrm_base_path: str = "data/india-latest.osrm", speed_csv_path: str = "data/osrm_segment_speeds.csv") -> bool:
    """
    Executes osrm-customize via subprocess to inject dynamic segment speed updates into OSRM engine.
    """
    if not os.path.exists(speed_csv_path):
        logger.error(f"[OSRM Customize] Speed file missing at '{speed_csv_path}'")
        return False

    cmd = ["osrm-customize", osrm_base_path, f"--segment-speed-file={speed_csv_path}"]
    logger.info(f"[OSRM Customize] Running command: {' '.join(cmd)}")

    try:
        # Dry-run / real subprocess call
        if shutil_which("osrm-customize"):
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"[OSRM Customize] Success: {res.stdout}")
            return True
        else:
            logger.warning("[OSRM Customize] osrm-customize binary not found in system PATH. Dry-run export succeeded.")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[OSRM Customize] Failed with exit code {e.returncode}: {e.stderr}")
        return False


def shutil_which(cmd: str) -> Optional[str]:
    import shutil
    return shutil.which(cmd)


if __name__ == "__main__":
    csv_file = generate_osrm_traffic_file()
    apply_osrm_customize(speed_csv_path=csv_file)

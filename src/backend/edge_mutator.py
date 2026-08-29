"""
Dynamic Edge-Weight Mutator Job (Member B - Prompt 2)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Recalculates operational dynamic edge costs (`dynamic_cost`, `dynamic_reverse_cost`)
in the road network graph based on incoming ML hazard probabilities.

Formula & Rules:
  - hazard_prob >= 0.70            -> dynamic_cost = 999999.0 (CRITICAL_AVOID: effectively blocked)
  - 0.35 <= hazard_prob < 0.70     -> dynamic_cost = cost * (1 + 5 * (hazard_prob ^ 2)) (WARNING_SLOW)
  - hazard_prob < 0.35             -> dynamic_cost = cost (SAFE: base travel time)

Guarantees transactional atomicity (all-or-nothing rollback) to prevent partial graph corruption.
"""

import sqlite3
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from src.backend.db import db_instance, HAS_PSYCOPG2, DB_URL

logger = logging.getLogger("MargSetu.EdgeMutator")
logging.basicConfig(level=logging.INFO)

# Exact PostGIS SQL UPDATE Query as specified in Prompt 2
POSTGIS_UPDATE_SQL = """
UPDATE road_edges
SET 
    hazard_prob = :hazard_prob,
    dynamic_cost = CASE
        WHEN :hazard_prob >= 0.70 THEN 999999.0
        WHEN :hazard_prob >= 0.35 THEN cost * (1.0 + 5.0 * POWER(:hazard_prob, 2))
        ELSE cost
    END,
    dynamic_reverse_cost = CASE
        WHEN :hazard_prob >= 0.70 THEN 999999.0
        WHEN :hazard_prob >= 0.35 THEN reverse_cost * (1.0 + 5.0 * POWER(:hazard_prob, 2))
        ELSE reverse_cost
    END,
    last_updated = CURRENT_TIMESTAMP
WHERE segment_id = :segment_id;
"""


def calculate_dynamic_cost(base_cost: float, hazard_prob: float) -> float:
    """
    Computes mutated dynamic edge cost from base travel cost and hazard probability.
    """
    if hazard_prob >= 0.70:
        return 999999.0
    elif hazard_prob >= 0.35:
        return round(float(base_cost * (1.0 + 5.0 * (hazard_prob ** 2))), 4)
    return round(float(base_cost), 4)


def update_dynamic_edge_weights(hazard_updates: List[Dict[str, Any]], db_conn=None) -> Dict[str, Any]:
    """
    Atomically updates hazard probabilities and dynamic costs for a batch of road segments.

    :param hazard_updates: List of dicts, e.g. [{"segment_id": "NH10_SEG_003", "hazard_probability": 0.85}, ...]
    :param db_conn: Optional connection override for custom database instances.
    :return: Summary dictionary of updated segments count and status.
    """
    if not hazard_updates:
        return {"status": "skipped", "updated_count": 0}

    conn = db_conn if db_conn is not None else db_instance.conn
    cursor = conn.cursor()

    try:
        # Begin transaction
        updated_records = 0
        timestamp_str = datetime.utcnow().isoformat()

        for update in hazard_updates:
            seg_id = update["segment_id"]
            haz_prob = float(update["hazard_probability"])
            model_ver = update.get("model_version", "xgb-1.0")

            # 1. Update road_edges dynamic cost
            if isinstance(conn, sqlite3.Connection):
                # SQLite syntax
                cursor.execute("""
                    SELECT cost, reverse_cost FROM road_edges WHERE segment_id = ?
                """, (seg_id,))
                row = cursor.fetchone()
                if row:
                    base_cost = row["cost"]
                    base_rev_cost = row["reverse_cost"]
                    dyn_cost = calculate_dynamic_cost(base_cost, haz_prob)
                    dyn_rev_cost = calculate_dynamic_cost(base_rev_cost, haz_prob)

                    cursor.execute("""
                        UPDATE road_edges
                        SET hazard_prob = ?,
                            dynamic_cost = ?,
                            dynamic_reverse_cost = ?,
                            last_updated = ?
                        WHERE segment_id = ?
                    """, (haz_prob, dyn_cost, dyn_rev_cost, timestamp_str, seg_id))
                    updated_records += 1
            else:
                # PostgreSQL / PostGIS execution
                cursor.execute(POSTGIS_UPDATE_SQL, {
                    "hazard_prob": haz_prob,
                    "segment_id": seg_id
                })
                updated_records += 1

            # 2. Append audit trail record to hazard_scores table
            if isinstance(conn, sqlite3.Connection):
                cursor.execute("""
                    INSERT INTO hazard_scores (segment_id, timestamp, hazard_probability, model_version)
                    VALUES (?, ?, ?, ?)
                """, (seg_id, timestamp_str, haz_prob, model_ver))
            else:
                cursor.execute("""
                    INSERT INTO hazard_scores (segment_id, timestamp, hazard_probability, model_version)
                    VALUES (%s, CURRENT_TIMESTAMP, %s, %s)
                """, (seg_id, haz_prob, model_ver))

        # Commit entire transaction atomically
        conn.commit()
        logger.info(f"[EdgeMutator] Successfully updated dynamic edge costs for {updated_records} road segments.")
        return {
            "status": "success",
            "updated_count": updated_records,
            "timestamp": timestamp_str
        }

    except Exception as e:
        # Rollback transaction on failure to ensure data consistency
        conn.rollback()
        logger.error(f"[EdgeMutator] Error updating dynamic costs. Transaction rolled back! Error: {e}")
        raise RuntimeError(f"Edge weight update failed: {e}")


def sync_hazard_scores_from_ml_service(ml_batch_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bridge function taking prediction output from Member A's FastAPI POST /predict/batch endpoint
    and mutating graph edge costs in the database.
    """
    predictions = ml_batch_response.get("predictions", [])
    updates = [
        {
            "segment_id": item["segment_id"],
            "hazard_probability": item["hazard_probability"]
        }
        for item in predictions
    ]
    return update_dynamic_edge_weights(updates)


if __name__ == "__main__":
    # Test batch mutation
    test_updates = [
        {"segment_id": "NH10_SEG_002", "hazard_probability": 0.65},
        {"segment_id": "NH10_SEG_003", "hazard_probability": 0.88}
    ]
    res = update_dynamic_edge_weights(test_updates)
    print(res)

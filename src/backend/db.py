"""
Database Access Layer & Road Graph Storage (Member B)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Provides database connectivity to PostgreSQL/PostGIS with fallback to an in-memory
SQLite/GeoPandas relational engine for standalone demonstration and unit testing.
"""

import os
import sqlite3
import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# PostgreSQL driver attempt
HAS_PSYCOPG2 = False
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    pass

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/margsetu_db")


class InMemoryRoadNetworkDB:
    """
    In-Memory Spatial Relational Database representing PostgreSQL/PostGIS tables
    for zero-dependency standalone execution & unit testing.
    """
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        self._populate_sample_ner_network()

    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE road_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                segment_id TEXT UNIQUE NOT NULL,
                source INTEGER NOT NULL,
                target INTEGER NOT NULL,
                start_lat REAL NOT NULL,
                start_lng REAL NOT NULL,
                end_lat REAL NOT NULL,
                end_lng REAL NOT NULL,
                length_km REAL NOT NULL,
                base_speed_kmh REAL NOT NULL DEFAULT 40.0,
                cost REAL NOT NULL,
                reverse_cost REAL NOT NULL,
                hazard_prob REAL NOT NULL DEFAULT 0.0,
                dynamic_cost REAL NOT NULL,
                dynamic_reverse_cost REAL NOT NULL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE hazard_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                segment_id TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                hazard_probability REAL NOT NULL,
                model_version TEXT DEFAULT 'xgb-1.0'
            );
        """)
        cursor.execute("""
            CREATE TABLE crowdsource_reports (
                id TEXT PRIMARY KEY,
                segment_id TEXT,
                reporter_id TEXT NOT NULL,
                photo_url TEXT,
                report_type TEXT NOT NULL,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                submitted_at TEXT NOT NULL,
                synced_at TEXT DEFAULT CURRENT_TIMESTAMP,
                verified INTEGER DEFAULT 0
            );
        """)
        cursor.execute("""
            CREATE TABLE vehicles (
                id TEXT PRIMARY KEY,
                driver_name TEXT NOT NULL,
                current_lat REAL NOT NULL,
                current_lng REAL NOT NULL,
                last_ping_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def _populate_sample_ner_network(self):
        """
        Populates a realistic sample North Eastern Region road network graph
        (e.g., NH-10 corridor connecting Siliguri -> Rangpo -> Gangtok -> Nathu La pass).
        Nodes:
          1: Siliguri Junction (26.7271, 88.3953)
          2: Sevoke Bridge (26.8900, 88.4700)
          3: Kalimpong Fork (27.0600, 88.4700)
          4: Rangpo Border Checkpost (27.1764, 88.5341)
          5: Singtam Logistics Hub (27.2300, 88.5000)
          6: Gangtok Capital (27.3389, 88.6065)
          7: Mangan North Sikkim (27.5000, 88.5300)
          8: Dikchu Bypass (27.3800, 88.5200)
        """
        nodes = {
            1: (26.7271, 88.3953),
            2: (26.8900, 88.4700),
            3: (27.0600, 88.4700),
            4: (27.1764, 88.5341),
            5: (27.2300, 88.5000),
            6: (27.3389, 88.6065),
            7: (27.5000, 88.5300),
            8: (27.3800, 88.5200)
        }

        # Edges (source, target, segment_id, length_km, base_speed, initial_hazard)
        edges_data = [
            (1, 2, "NH10_SEG_001", 22.0, 50.0, 0.10),
            (2, 3, "NH10_SEG_002", 28.0, 40.0, 0.45), # Moderate hazard (Teesta riverbank)
            (3, 4, "NH10_SEG_003", 18.0, 35.0, 0.82), # Critical hazard (Landslide zone)
            (4, 5, "NH10_SEG_004", 12.0, 40.0, 0.15),
            (5, 6, "NH10_SEG_005", 26.0, 45.0, 0.20),
            # Bypass alternative route avoiding NH10_SEG_003
            (2, 8, "ALT_BYPASS_001", 35.0, 35.0, 0.12),
            (8, 5, "ALT_BYPASS_002", 24.0, 35.0, 0.18),
            (6, 7, "NORTH_HIGHWAY_001", 48.0, 30.0, 0.65)
        ]

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM road_edges;")
        for src, tgt, seg_id, length_km, speed_kmh, haz_prob in edges_data:
            s_lat, s_lng = nodes[src]
            e_lat, e_lng = nodes[tgt]
            cost_min = (length_km / speed_kmh) * 60.0 # Base cost in minutes

            # Calculate initial dynamic cost
            if haz_prob >= 0.70:
                dyn_cost = 999999.0
            elif haz_prob >= 0.35:
                dyn_cost = cost_min * (1.0 + 5.0 * (haz_prob ** 2))
            else:
                dyn_cost = cost_min

            cursor.execute("""
                INSERT INTO road_edges (
                    segment_id, source, target, start_lat, start_lng, end_lat, end_lng,
                    length_km, base_speed_kmh, cost, reverse_cost, hazard_prob,
                    dynamic_cost, dynamic_reverse_cost
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                seg_id, src, tgt, s_lat, s_lng, e_lat, e_lng,
                length_km, speed_kmh, cost_min, cost_min, haz_prob,
                dyn_cost, dyn_cost
            ))

        self.conn.commit()

    def get_all_edges(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM road_edges")
        return [dict(row) for row in cursor.fetchall()]


# Global database instance singleton
db_instance = InMemoryRoadNetworkDB()

"""
Unit & Integration Test Suite for Member B (Backend & Routing Track)
"""

import unittest
import uuid
import json
from fastapi.testclient import TestClient

from src.backend.db import InMemoryRoadNetworkDB
from src.backend.edge_mutator import update_dynamic_edge_weights, calculate_dynamic_cost
from src.backend.routing_api import snap_coordinate_to_nearest_node, haversine_distance_km
from src.backend.osrm_export import calculate_osrm_adjusted_speed, generate_osrm_traffic_file
from src.backend.app import app


class TestBackendMemberB(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_db = InMemoryRoadNetworkDB()

    def test_dynamic_cost_formula(self):
        # Base cost = 30 min
        base = 30.0
        self.assertEqual(calculate_dynamic_cost(base, 0.10), 30.0) # SAFE
        self.assertEqual(calculate_dynamic_cost(base, 0.34), 30.0) # SAFE
        
        # WARNING_SLOW: 30 * (1 + 5 * 0.5^2) = 30 * 2.25 = 67.5
        self.assertAlmostEqual(calculate_dynamic_cost(base, 0.50), 67.5, places=2)
        
        # CRITICAL_AVOID: >= 0.70 -> 999999.0
        self.assertEqual(calculate_dynamic_cost(base, 0.75), 999999.0)

    def test_edge_mutator_transactional_update(self):
        updates = [
            {"segment_id": "NH10_SEG_001", "hazard_probability": 0.50},
            {"segment_id": "NH10_SEG_004", "hazard_probability": 0.80}
        ]
        res = update_dynamic_edge_weights(updates, db_conn=self.test_db.conn)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["updated_count"], 2)

        # Verify DB state after mutation
        cursor = self.test_db.conn.cursor()
        cursor.execute("SELECT dynamic_cost FROM road_edges WHERE segment_id = 'NH10_SEG_004'")
        row = cursor.fetchone()
        self.assertEqual(row["dynamic_cost"], 999999.0)

    def test_coordinate_snapping(self):
        # Coordinates near Siliguri node (26.7271, 88.3953)
        node = snap_coordinate_to_nearest_node(26.72, 88.39)
        self.assertEqual(node, 1)

    def test_safe_route_endpoint_success(self):
        # Siliguri (26.7271, 88.3953) to Gangtok (27.3389, 88.6065) via bypass
        response = self.client.get("/route-safe?source_lat=26.7271&source_lng=88.3953&target_lat=27.3389&target_lng=88.6065")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data["region_isolated"])
        self.assertGreater(data["segments_count"], 0)
        self.assertIn("route_geojson", data)
        self.assertEqual(data["route_geojson"]["type"], "FeatureCollection")

    def test_safe_route_isolated_disaster_alert(self):
        from src.backend.db import db_instance
        cursor = db_instance.conn.cursor()
        cursor.execute("UPDATE road_edges SET hazard_prob = 0.95, dynamic_cost = 999999.0, dynamic_reverse_cost = 999999.0")
        db_instance.conn.commit()

        try:
            response = self.client.get("/route-safe?source_lat=26.7271&source_lng=88.3953&target_lat=27.3389&target_lng=88.6065")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["region_isolated"])
            self.assertIn("CRITICAL DISASTER ALERT", data["isolation_warning"])
        finally:
            # Reset network graph state
            db_instance._populate_sample_ner_network()

    def test_osrm_speed_export(self):
        csv_path = generate_osrm_traffic_file(output_csv_path="data/test_osrm_speeds.csv")
        self.assertTrue(json.dumps(csv_path).endswith("test_osrm_speeds.csv\""))

    def test_sync_up_endpoint_idempotency(self):
        report_uuid = str(uuid.uuid4())
        payload = {
            "reports": [
                {
                    "id": report_uuid,
                    "segment_id": "NH10_SEG_002",
                    "reporter_id": "DRIVER_42",
                    "report_type": "blockage",
                    "lat": 27.0600,
                    "lng": 88.4700,
                    "submitted_at": "2026-08-29T12:00:00Z"
                }
            ]
        }

        # First upload
        res1 = self.client.post("/api/v1/sync/up", json=payload)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["items"][0]["status"], "SUCCESS")

        # Second upload (idempotent retry)
        res2 = self.client.post("/api/v1/sync/up", json=payload)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["items"][0]["status"], "DUPLICATE_UPSERTED")

    def test_sync_down_endpoint(self):
        res = self.client.get("/api/v1/sync/down?since=2026-08-01T00:00:00Z")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("hazard_updates", data)
        self.assertGreater(data["changed_segments_count"], 0)


if __name__ == "__main__":
    unittest.main()

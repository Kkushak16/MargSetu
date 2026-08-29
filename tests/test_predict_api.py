"""
Unit tests for FastAPI Inference Router (Member A - Prompt 4)
"""

import unittest
from fastapi.testclient import TestClient
from src.ml.predict_api import app, determine_status


class TestPredictAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_determine_status_thresholds(self):
        self.assertEqual(determine_status(0.10), "SAFE")
        self.assertEqual(determine_status(0.34), "SAFE")
        self.assertEqual(determine_status(0.35), "WARNING_SLOW")
        self.assertEqual(determine_status(0.69), "WARNING_SLOW")
        self.assertEqual(determine_status(0.70), "CRITICAL_AVOID")
        self.assertEqual(determine_status(0.95), "CRITICAL_AVOID")

    def test_health_endpoint(self):
        with TestClient(app) as client:
            response = client.get("/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            self.assertTrue(data["model_loaded"])

    def test_predict_single_segment(self):
        payload = {
            "segment_id": "NH10_SEG_042",
            "slope_deg": 38.5,
            "twi": 11.2,
            "curvature": 0.015,
            "dist_to_fault_m": 120.0,
            "soil_saturation_pct": 88.0,
            "forecast_rain_3h": 65.0,
            "ari_7d": 160.0,
            "aspect": 140.0,
            "ndvi": 0.25
        }

        with TestClient(app) as client:
            response = client.post("/predict", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()

            self.assertEqual(data["segment_id"], "NH10_SEG_042")
            self.assertIn(data["status"], ["SAFE", "WARNING_SLOW", "CRITICAL_AVOID"])
            self.assertGreaterEqual(data["hazard_probability"], 0.0)
            self.assertLessEqual(data["hazard_probability"], 1.0)
            self.assertEqual(len(data["top_shap_features"]), 3)
            self.assertLess(data["latency_ms"], 200.0) # Sub-200ms in test environment

    def test_predict_batch_segments(self):
        payload = {
            "segments": [
                {
                    "segment_id": "SEG_01",
                    "slope_deg": 10.0,
                    "twi": 4.0,
                    "dist_to_fault_m": 2000.0,
                    "soil_saturation_pct": 30.0,
                    "forecast_rain_3h": 0.0,
                    "ari_7d": 10.0
                },
                {
                    "segment_id": "SEG_02",
                    "slope_deg": 45.0,
                    "twi": 14.0,
                    "dist_to_fault_m": 50.0,
                    "soil_saturation_pct": 95.0,
                    "forecast_rain_3h": 85.0,
                    "ari_7d": 210.0
                }
            ]
        }

        with TestClient(app) as client:
            response = client.post("/predict/batch", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["total_segments"], 2)
            self.assertEqual(len(data["predictions"]), 2)
            self.assertEqual(data["predictions"][0]["segment_id"], "SEG_01")
            self.assertEqual(data["predictions"][1]["segment_id"], "SEG_02")


if __name__ == "__main__":
    unittest.main()

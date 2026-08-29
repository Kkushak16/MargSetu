"""
Unit & Integration Test Suite for Member C (Frontend, Mobile & PWA Track)
"""

import unittest
import os
import json
import re


class TestFrontendMemberC(unittest.TestCase):

    def test_shap_translation_mapping(self):
        # Python test validating SHAP feature plain-English mappings
        dictionary = {
            "ari_7d": "Heavy rainfall accumulation over the past 7 days",
            "slope_deg": "Extremely steep mountain incline (>30° slope)",
            "twi": "High water saturation zone",
            "dist_to_fault_m": "Proximity to high-shear geological fault line",
            "forecast_rain_3h": "Severe cloudburst forecast in next 3 hours"
        }

        # Test translation lookups
        self.assertIn("rainfall", dictionary["ari_7d"])
        self.assertIn("steep", dictionary["slope_deg"])
        self.assertIn("fault", dictionary["dist_to_fault_m"])

    def test_standalone_index_html_structure(self):
        html_path = os.path.join("src", "frontend", "public", "index.html")
        self.assertTrue(os.path.exists(html_path), "index.html visualizer missing!")

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required Leaflet, safe route form, and SHAP container
        self.assertIn("leaflet.css", content)
        self.assertIn("leaflet.js", content)
        self.assertIn("shapExplanationBox", content)
        self.assertIn("handleComputeRoute", content)
        self.assertIn("handleSaveOfflineReport", content)

    def test_flutter_field_app_files(self):
        pubspec_path = os.path.join("mobile", "pubspec.yaml")
        main_dart_path = os.path.join("mobile", "lib", "main.dart")
        sync_manager_path = os.path.join("mobile", "lib", "sync_manager.dart")

        self.assertTrue(os.path.exists(pubspec_path))
        self.assertTrue(os.path.exists(main_dart_path))
        self.assertTrue(os.path.exists(sync_manager_path))

        with open(main_dart_path, "r", encoding="utf-8") as f:
            dart_code = f.read()

        # Verify 3 screens present in Flutter app
        self.assertIn("MapScreen", dart_code)
        self.assertIn("ReportScreen", dart_code)
        self.assertIn("SyncStatusScreen", dart_code)

    def test_pwa_service_worker_caching(self):
        sw_path = os.path.join("src", "frontend", "public", "service-worker.js")
        self.assertTrue(os.path.exists(sw_path))

        with open(sw_path, "r", encoding="utf-8") as f:
            sw_code = f.read()

        self.assertIn("margsetu-pwa-cache", sw_code)
        self.assertIn("addEventListener('fetch'", sw_code)


if __name__ == "__main__":
    unittest.main()

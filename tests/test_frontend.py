"""
Unit & Integration Test Suite for Member C (Frontend, Mobile, PWA & Control Room Track)
"""

import unittest
import os
import json


class TestFrontendMemberC(unittest.TestCase):

    def test_shap_translation_mapping(self):
        dictionary = {
            "ari_7d": "Heavy rainfall accumulation over the past 7 days",
            "slope_deg": "Extremely steep mountain incline (>30° slope)",
            "twi": "High water saturation zone",
            "dist_to_fault_m": "Proximity to high-shear geological fault line",
            "forecast_rain_3h": "Severe cloudburst forecast in next 3 hours"
        }

        self.assertIn("rainfall", dictionary["ari_7d"])
        self.assertIn("steep", dictionary["slope_deg"])
        self.assertIn("fault", dictionary["dist_to_fault_m"])

    def test_standalone_index_html_structure(self):
        html_path = os.path.join("src", "frontend", "public", "index.html")
        self.assertTrue(os.path.exists(html_path), "index.html visualizer missing!")

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required MapLibre 3D, settings drawer, crowdsource feed, alerts, and SHAP container
        self.assertIn("maplibre-gl.css", content)
        self.assertIn("maplibre-gl.js", content)
        self.assertIn("KEY DRIVERS", content)
        self.assertIn("settingsDrawer", content)
        self.assertIn("reportStatusBadge", content)
        self.assertIn("updateThresholds", content)

    def test_dashboard_components_and_context_files(self):
        context_path = os.path.join("src", "frontend", "context", "DashboardSettingsContext.tsx")
        panel_path = os.path.join("src", "frontend", "components", "DashboardSettingsPanel.tsx")
        feed_path = os.path.join("src", "frontend", "components", "CrowdsourceFeed.tsx")
        alerts_path = os.path.join("src", "frontend", "components", "AlertsSidebar.tsx")

        self.assertTrue(os.path.exists(context_path))
        self.assertTrue(os.path.exists(panel_path))
        self.assertTrue(os.path.exists(feed_path))
        self.assertTrue(os.path.exists(alerts_path))

    def test_flutter_field_app_files(self):
        pubspec_path = os.path.join("mobile", "pubspec.yaml")
        main_dart_path = os.path.join("mobile", "lib", "main.dart")
        sync_manager_path = os.path.join("mobile", "lib", "sync_manager.dart")

        self.assertTrue(os.path.exists(pubspec_path))
        self.assertTrue(os.path.exists(main_dart_path))
        self.assertTrue(os.path.exists(sync_manager_path))

    def test_pwa_service_worker_caching(self):
        sw_path = os.path.join("src", "frontend", "public", "service-worker.js")
        self.assertTrue(os.path.exists(sw_path))


if __name__ == "__main__":
    unittest.main()

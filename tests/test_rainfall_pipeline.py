"""
Unit tests for Antecedent Rainfall Index & Dynamic Feature Builder (Member A - Prompt 2)
"""

import unittest
import pandas as pd
import numpy as np
from src.ml.rainfall_pipeline import (
    compute_antecedent_rainfall,
    build_dynamic_rainfall_features,
    generate_synthetic_rainfall_data
)


class TestRainfallPipeline(unittest.TestCase):

    def test_ari_sequence_1_zero_rain(self):
        """Sequence 1: Dry spell with 0mm rain over 7 days."""
        seq = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ari = compute_antecedent_rainfall(seq, decay_factor=0.5)
        self.assertAlmostEqual(ari, 0.0, places=4)

    def test_ari_sequence_2_constant_rain(self):
        """Sequence 2: Constant 10mm daily rainfall over 7 days."""
        seq = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
        ari = compute_antecedent_rainfall(seq, decay_factor=0.5)
        # Sum of weights * 10 = 40.1788
        self.assertAlmostEqual(ari, 40.1788, places=2)

    def test_ari_sequence_3_recent_cloudburst(self):
        """Sequence 3: Heavy recent cloudburst (100mm 1d ago, 50mm 2d ago, 20mm 3d ago)."""
        seq = [100.0, 50.0, 20.0, 0.0, 0.0, 0.0, 0.0]
        ari = compute_antecedent_rainfall(seq, decay_factor=0.5)
        # Expected: 100*1 + 50*(1/sqrt(2)) + 20*(1/sqrt(3)) = 146.9023
        self.assertAlmostEqual(ari, 146.9023, places=2)

    def test_ari_sequence_4_decay_ordering_impact(self):
        """Sequence 4: Verify that recent rain weighs heavier than older rain."""
        recent_storm = [100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        old_storm = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0]
        
        ari_recent = compute_antecedent_rainfall(recent_storm, decay_factor=0.5)
        ari_old = compute_antecedent_rainfall(old_storm, decay_factor=0.5)

        self.assertGreater(ari_recent, ari_old)
        self.assertAlmostEqual(ari_recent, 100.0, places=4)
        self.assertAlmostEqual(ari_old, 37.7964, places=2)

    def test_ari_invalid_input(self):
        """Verify validation errors for bad input lengths or negative values."""
        with self.assertRaises(ValueError):
            compute_antecedent_rainfall([10.0, 20.0]) # Length != 7

        with self.assertRaises(ValueError):
            compute_antecedent_rainfall([10.0] * 6 + [-5.0]) # Negative rainfall

    def test_build_dynamic_rainfall_features(self):
        rainfall_df = generate_synthetic_rainfall_data(stations=["STATION_A", "STATION_B"], days=10)
        mapping = {"SEG_01": "STATION_A", "SEG_02": "STATION_B"}
        
        df_out = build_dynamic_rainfall_features(rainfall_df, mapping)
        self.assertEqual(len(df_out), 2)
        self.assertIn("ari_7d", df_out.columns)
        self.assertIn("forecast_rain_3h", df_out.columns)
        self.assertTrue((df_out["ari_7d"] >= 0.0).all())


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for DEM Feature Extraction Pipeline (Member A - Prompt 1)
"""

import unittest
import numpy as np
import pandas as pd
from src.ml.dem_pipeline import (
    compute_slope_aspect_curvature,
    compute_twi,
    extract_features_for_road_segments,
    generate_synthetic_dem
)


class TestDEMPipeline(unittest.TestCase):

    def setUp(self):
        self.dem = generate_synthetic_dem(rows=50, cols=50, cell_size_m=30.0)

    def test_slope_aspect_curvature_shapes(self):
        slope, aspect, curv = compute_slope_aspect_curvature(self.dem, cell_size_m=30.0)
        self.assertEqual(slope.shape, (50, 50))
        self.assertEqual(aspect.shape, (50, 50))
        self.assertEqual(curv.shape, (50, 50))

        # Check value constraints
        self.assertTrue(np.all(slope >= 0.0) and np.all(slope <= 90.0))
        self.assertTrue(np.all(aspect >= 0.0) and np.all(aspect <= 360.0))

    def test_twi_computation(self):
        slope, _, _ = compute_slope_aspect_curvature(self.dem, cell_size_m=30.0)
        twi = compute_twi(slope, cell_size_m=30.0)
        self.assertEqual(twi.shape, (50, 50))
        self.assertTrue(np.all(twi >= 0.0))

    def test_road_segment_extraction(self):
        sample_roads = [
            {"segment_id": "SEG_TEST_001", "start_coords": (100.0, 100.0), "end_coords": (400.0, 400.0)},
            {"segment_id": "SEG_TEST_002", "start_coords": (500.0, 200.0), "end_coords": (800.0, 300.0)}
        ]
        df = extract_features_for_road_segments(self.dem, sample_roads, cell_size_m=30.0)
        self.assertEqual(len(df), 2)
        expected_cols = {"road_segment_id", "slope_deg", "aspect", "curvature", "twi", "dist_to_fault_m"}
        self.assertTrue(expected_cols.issubset(set(df.columns)))
        self.assertEqual(df["road_segment_id"].tolist(), ["SEG_TEST_001", "SEG_TEST_002"])


if __name__ == "__main__":
    unittest.main()

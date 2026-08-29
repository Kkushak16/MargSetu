"""
Unit tests for XGBoost Model Training and Validation Metrics (Member A - Prompt 3)
"""

import os
import unittest
import pandas as pd
from src.ml.train import (
    generate_synthetic_training_dataset,
    train_xgboost_hazard_model,
    calculate_recall_at_precision
)


class TestTrainModel(unittest.TestCase):

    def setUp(self):
        self.dataset_path = "data/test_landslide_set.csv"
        self.model_path = "models/test_hazard_xgb.json"

    def tearDown(self):
        if os.path.exists(self.dataset_path):
            os.remove(self.dataset_path)
        if os.path.exists(self.model_path):
            os.remove(self.model_path)

    def test_synthetic_dataset_generation(self):
        df = generate_synthetic_training_dataset(num_samples=200, output_csv=self.dataset_path)
        self.assertEqual(len(df), 200)
        self.assertIn("basin_id", df.columns)
        self.assertIn("label", df.columns)
        self.assertTrue(set(df["label"].unique()).issubset({0, 1}))

    def test_recall_at_precision(self):
        y_true = [1, 1, 1, 0, 0, 0, 0, 0]
        y_probs = [0.95, 0.85, 0.75, 0.20, 0.15, 0.10, 0.05, 0.01]
        rec = calculate_recall_at_precision(y_true, y_probs, target_precision=0.90)
        self.assertGreater(rec, 0.0)

    def test_train_model(self):
        df = generate_synthetic_training_dataset(num_samples=150, output_csv=self.dataset_path)
        model, metrics = train_xgboost_hazard_model(
            data_csv_path=self.dataset_path,
            model_output_path=self.model_path,
            n_splits=3
        )

        self.assertTrue(os.path.exists(self.model_path))
        self.assertIn("mean_pr_auc", metrics)
        self.assertIn("mean_recall_at_90_precision", metrics)
        self.assertGreater(metrics["mean_pr_auc"], 0.50)


if __name__ == "__main__":
    unittest.main()

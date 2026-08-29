"""
Test Runner Script for MargSetu Member A ML Track
Executes all unit and integration tests across DEM pipeline, Rainfall pipeline, XGBoost training, and FastAPI endpoints.
"""

import sys
import unittest

if __name__ == "__main__":
    print("=" * 70)
    print("      RUNNING MARGSETU MEMBER A (ML TRACK) TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 70)
        print(" [SUCCESS] All Member A ML pipeline tests passed successfully!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print(" [FAILURE] Test suite encountered failures or errors.")
        print("=" * 70)
        sys.exit(1)

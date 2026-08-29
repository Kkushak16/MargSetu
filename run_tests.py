"""
Master Test Runner Script for MargSetu (Member A + Member B Tracks)
Executes all unit and integration tests across ML pipelines, PostGIS schema, edge mutator, safe routing engine, OSRM exporter, and sync endpoints.
"""

import sys
import unittest

if __name__ == "__main__":
    print("=" * 75)
    print("     RUNNING MARGSETU INTEGRATED TEST SUITE (MEMBER A + MEMBER B)")
    print("=" * 75)

    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 75)
        print(" [SUCCESS] All Member A & Member B test suites passed successfully!")
        print("=" * 75)
        sys.exit(0)
    else:
        print("\n" + "=" * 75)
        print(" [FAILURE] Test suite encountered failures or errors.")
        print("=" * 75)
        sys.exit(1)

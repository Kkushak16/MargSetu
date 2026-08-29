"""
Master Integrated Test Runner Script for MargSetu (Member A + Member B + Member C Tracks)
Executes all unit and integration tests across ML hazard model, PostGIS schema, edge mutator,
safe routing engine, offline sync manager, GIS frontend, PWA service worker, and Flutter shell.
"""

import sys
import unittest

if __name__ == "__main__":
    print("=" * 80)
    print("  RUNNING MARGSETU INTEGRATED TEST SUITE (MEMBER A + MEMBER B + MEMBER C)")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 80)
        print(" [SUCCESS] All Member A, Member B, & Member C test suites passed successfully!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print(" [FAILURE] Test suite encountered failures or errors.")
        print("=" * 80)
        sys.exit(1)

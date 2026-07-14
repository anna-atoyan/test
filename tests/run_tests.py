#!/usr/bin/env python3
"""
Test runner script for logsum tests.

This script provides convenient ways to run different test categories.
"""

import sys
import subprocess
from pathlib import Path


def run_tests(test_filter=None, verbose=True):
    """Run pytest with optional test filter."""
    cmd = ["pytest", "tests/test_logsum.py"]
    
    if verbose:
        cmd.append("-v")
    
    if test_filter:
        cmd.extend(["-k", test_filter])
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        category = sys.argv[1]
        
        categories = {
            "normalization": "normalization",
            "grouping": "grouping",
            "aggregation": "aggregation",
            "missing": "missing_level",
            "malformed": "malformed",
            "empty": "empty",
            "invalid": "invalid",
            "sorting": "sorting",
            "csv": "csv and not invalid",
            "cli": "cli or flag",
            "integration": "complex or output_csv_structure"
        }
        
        if category in categories:
            print(f"Running {category} tests...")
            return run_tests(categories[category])
        elif category == "all":
            print("Running all tests...")
            return run_tests()
        elif category == "help":
            print("Usage: python run_tests.py [category]")
            print("\nAvailable categories:")
            for cat in sorted(categories.keys()):
                print(f"  {cat}")
            print("  all")
            print("  help")
            return 0
        else:
            print(f"Unknown category: {category}")
            print("Run 'python run_tests.py help' for available categories")
            return 1
    else:
        print("Running all tests...")
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())

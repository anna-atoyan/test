#!/usr/bin/env python3
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--output')

try:
    args = parser.parse_args(['--help'])
    print("Parsed successfully")
except SystemExit as e:
    print(f"SystemExit caught with code: {e.code}")
    sys.exit(e.code)

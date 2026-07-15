import sys
import argparse

p = argparse.ArgumentParser()
p.add_argument('--help-test', action='help')
try:
    p.parse_args(['--help'])
except SystemExit as e:
    print(f"Exit code: {e.code}")
    sys.exit(0)

#!/bin/bash
# Simulate exact GitHub CI workflow locally

echo "==================================="
echo "Simulating GitHub CI Workflow"
echo "==================================="
echo ""

echo "Step 1: Install dependencies"
python -m pip install --upgrade pip --quiet
pip install ruff pytest --quiet
pip install -e . --quiet
echo "✅ Dependencies installed"
echo ""

echo "Step 2: Run ruff check"
ruff check .
if [ $? -eq 0 ]; then
    echo "✅ Ruff check passed"
else
    echo "❌ Ruff check failed"
    exit 1
fi
echo ""

echo "Step 3: Run tests"
pytest -v
if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "✅ ALL CI STEPS PASSED!"
    echo "==================================="
else
    echo ""
    echo "==================================="
    echo "❌ TESTS FAILED"
    echo "==================================="
    exit 1
fi

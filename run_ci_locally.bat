@echo off
REM Simulate exact GitHub CI workflow locally (Windows)

echo ===================================
echo Simulating GitHub CI Workflow
echo ===================================
echo.

echo Step 1: Install dependencies
python -m pip install --upgrade pip --quiet
pip install ruff pytest --quiet
pip install -e . --quiet
echo ✅ Dependencies installed
echo.

echo Step 2: Run ruff check
ruff check .
if %errorlevel% neq 0 (
    echo ❌ Ruff check failed
    exit /b 1
)
echo ✅ Ruff check passed
echo.

echo Step 3: Run tests
pytest -v
if %errorlevel% neq 0 (
    echo.
    echo ===================================
    echo ❌ TESTS FAILED
    echo ===================================
    exit /b 1
)

echo.
echo ===================================
echo ✅ ALL CI STEPS PASSED!
echo ===================================

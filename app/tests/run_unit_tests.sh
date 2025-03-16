#!/bin/bash
# Special script for running unit tests that avoids file descriptor issues
# and provides more diagnostic information

# Don't use set -e here as we want to collect failure information
# instead of exiting immediately on errors

echo "==========================================================="
echo "    ENHANCED UNIT TEST RUNNER FOR CONTAINER ENVIRONMENT    "
echo "==========================================================="

# Create central test results directory - same location as run_tests.sh
RESULTS_DIR="/app/test-results"
mkdir -p "$RESULTS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$RESULTS_DIR/unit_tests_${TIMESTAMP}.log"

echo "[$(date)] - Starting test execution" | tee -a "$LOG_FILE"

# Log Python and environment information
echo "[*] Python version:"
python --version
echo "[*] Pytest version:"
python -m pytest --version
echo "[*] Environment variables:"
echo "PYTHONPATH: $PYTHONPATH"
echo "PYTHONUNBUFFERED: $PYTHONUNBUFFERED"
echo "USER: $USER"

# Clear any previous pytest cache that might cause issues
echo "[*] Cleaning pytest cache..."
find /app -name "__pycache__" -type d -exec rm -rf {} +  2>/dev/null || true
find /app -name "*.pyc" -delete

# Set environment variables for safer test execution
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1  # Enable detailed traceback on segfaults/crashes
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTEST_ADDOPTS="-v --no-header"
export PYTHONIOENCODING=utf-8

echo "[*] Running unit tests with basic configuration and timeout..." | tee -a "$LOG_FILE"

# Move to the app directory to run tests
cd /app

# Run pytest with minimal plugins and a timeout
timeout 300 python -m pytest tests/unit \
  -v \
  --no-header \
  -p no:cacheprovider \
  -p no:capture \
  --tb=native \
  2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

echo "[$(date)] - Test execution completed with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"

if [ $EXIT_CODE -eq 124 ]; then
    echo "ERROR: Tests timed out after 300 seconds" | tee -a "$LOG_FILE"
elif [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: Tests failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"
    echo "Check the log file for details: $LOG_FILE"
else
    echo "SUCCESS: Tests passed successfully" | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE 
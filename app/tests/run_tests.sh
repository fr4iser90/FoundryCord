#!/bin/bash
# Test execution utility script for HomeLab Discord Bot

set -e

# Get the directory where the script is located to ensure consistent path resolution
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"

# Print diagnostic information
echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Define test execution order with relative paths
CORE_TESTS="$SCRIPT_DIR/unit/infrastructure/"
UNIT_TESTS="$SCRIPT_DIR/unit/"
INTEGRATION_TESTS="$SCRIPT_DIR/integration/"
FUNCTIONAL_TESTS="$SCRIPT_DIR/functional/"
PERFORMANCE_TESTS="$SCRIPT_DIR/performance/"

# Create central test results directory - accessible from host
RESULTS_DIR="/app/test-results"
mkdir -p "$RESULTS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/test_results_${TIMESTAMP}.txt"

# Log start of test execution
echo "[$(date)] Starting test execution..." | tee -a "$RESULTS_FILE"
echo "Test type: $1" | tee -a "$RESULTS_FILE"
echo "Environment: $(env | grep -i python)" | tee -a "$RESULTS_FILE"

# Verify directories exist before running tests
check_directory() {
    if [ ! -d "$1" ]; then
        echo "WARNING: Directory not found: $1"
        return 1
    fi
    return 0
}

# Function to run unit tests using the specialized script
run_unit_tests_safely() {
    echo "Running unit tests with specialized script for container environment..."
    
    # Use the specialized script that handles file descriptor issues
    if [ -f "$SCRIPT_DIR/run_unit_tests.sh" ]; then
        bash "$SCRIPT_DIR/run_unit_tests.sh"
        return $?
    else
        echo "WARNING: run_unit_tests.sh not found, falling back to standard method"
        
        # Special environment variables to avoid file descriptor issues
        export PYTHONUNBUFFERED=1
        
        # Clear any previous pytest cache that might cause issues
        find /app -name "__pycache__" -type d -exec rm -rf {} +  2>/dev/null || true
        find /app -name "*.pyc" -delete
        
        # Run pytest with basic options - avoid options that might not be supported
        cd "$SCRIPT_DIR"
        python -m pytest "$UNIT_TESTS" --ignore="$CORE_TESTS" -v
        
        return $?
    fi
}

# Function to safely run tests
run_tests_with_retry() {
    local test_path=$1
    local test_name=$2
    local max_retries=3
    local retry=0
    
    echo "Running $test_name tests..."
    
    # Special case for unit tests because of file descriptor issues
    if [ "$test_name" = "unit tests (excluding core tests)" ]; then
        run_unit_tests_safely
        return $?
    fi
    
    # For other test types, use standard pytest
    while [ $retry -lt $max_retries ]; do
        if python -m pytest $test_path -v; then
            return 0
        else
            echo "Test attempt $((retry+1)) failed, retrying..."
            sleep 1
            ((retry++))
        fi
    done
    
    echo "Tests failed after $max_retries attempts"
    return 1
}

case "$1" in
  all)
    echo "Running all tests in sequence from most critical to least critical..."
    
    if check_directory "$CORE_TESTS"; then
        echo "Running core infrastructure tests..."
        run_tests_with_retry "$CORE_TESTS" "core infrastructure"
        CORE_EXIT=$?
    else
        CORE_EXIT=0
    fi
    
    if [ $CORE_EXIT -eq 0 ] && check_directory "$UNIT_TESTS"; then
        echo "Running unit tests (excluding core tests)..."
        run_tests_with_retry "$UNIT_TESTS" "unit tests (excluding core tests)"
        UNIT_EXIT=$?
    else
        UNIT_EXIT=0
    fi
    
    if [ $UNIT_EXIT -eq 0 ] && check_directory "$INTEGRATION_TESTS"; then
        echo "Running integration tests..."
        run_tests_with_retry "$INTEGRATION_TESTS" "integration"
        INTEGRATION_EXIT=$?
    else
        INTEGRATION_EXIT=0
    fi
    
    if [ $INTEGRATION_EXIT -eq 0 ] && check_directory "$FUNCTIONAL_TESTS"; then
        echo "Running functional tests..."
        run_tests_with_retry "$FUNCTIONAL_TESTS" "functional"
        FUNCTIONAL_EXIT=$?
    else
        FUNCTIONAL_EXIT=0
    fi
    
    if [ $FUNCTIONAL_EXIT -eq 0 ] && check_directory "$PERFORMANCE_TESTS"; then
        echo "Running performance tests..."
        run_tests_with_retry "$PERFORMANCE_TESTS" "performance"
    fi
    ;;
  core)
    echo "Running core infrastructure tests..."
    check_directory "$CORE_TESTS" && run_tests_with_retry "$CORE_TESTS" "core infrastructure"
    ;;
  unit)
    echo "Running unit tests..."
    check_directory "$UNIT_TESTS" && run_tests_with_retry "$UNIT_TESTS" "unit tests (excluding core tests)"
    ;;
  integration)
    echo "Running integration tests..."
    check_directory "$INTEGRATION_TESTS" && run_tests_with_retry "$INTEGRATION_TESTS" "integration"
    ;;
  functional)
    echo "Running functional tests..."
    check_directory "$FUNCTIONAL_TESTS" && run_tests_with_retry "$FUNCTIONAL_TESTS" "functional"
    ;;
  performance)
    echo "Running performance tests..."
    check_directory "$PERFORMANCE_TESTS" && run_tests_with_retry "$PERFORMANCE_TESTS" "performance"
    ;;
  dashboard)
    echo "Running dashboard-related tests..."
    pytest -m dashboard
    ;;
  commands)
    echo "Running command-related tests..."
    pytest -m commands
    ;;
  coverage)
    echo "Running tests with coverage report..."
    pytest --cov=app --cov-report=html
    ;;
  *)
    echo "Usage: $0 {all|core|unit|integration|functional|performance|dashboard|commands|coverage}"
    exit 1
esac

# Save test results to the standard directory
echo "Test execution completed at $(date)" >> "$RESULTS_FILE"
echo "Results saved to: $RESULTS_FILE" 
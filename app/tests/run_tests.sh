#!/bin/bash
# Test execution utility script for HomeLab Discord Bot

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

# Verify directories exist before running tests
check_directory() {
    if [ ! -d "$1" ]; then
        echo "WARNING: Directory not found: $1"
        return 1
    fi
    return 0
}

case "$1" in
  all)
    echo "Running all tests in sequence from most critical to least critical..."
    
    if check_directory "$CORE_TESTS"; then
        echo "Running core infrastructure tests..."
        pytest "$CORE_TESTS"
        CORE_EXIT=$?
    else
        CORE_EXIT=0
    fi
    
    if [ $CORE_EXIT -eq 0 ] && check_directory "$UNIT_TESTS"; then
        echo "Running unit tests (excluding core tests)..."
        pytest "$UNIT_TESTS" --ignore="$CORE_TESTS"
        UNIT_EXIT=$?
    else
        UNIT_EXIT=0
    fi
    
    if [ $UNIT_EXIT -eq 0 ] && check_directory "$INTEGRATION_TESTS"; then
        echo "Running integration tests..."
        pytest "$INTEGRATION_TESTS"
        INTEGRATION_EXIT=$?
    else
        INTEGRATION_EXIT=0
    fi
    
    if [ $INTEGRATION_EXIT -eq 0 ] && check_directory "$FUNCTIONAL_TESTS"; then
        echo "Running functional tests..."
        pytest "$FUNCTIONAL_TESTS"
        FUNCTIONAL_EXIT=$?
    else
        FUNCTIONAL_EXIT=0
    fi
    
    if [ $FUNCTIONAL_EXIT -eq 0 ] && check_directory "$PERFORMANCE_TESTS"; then
        echo "Running performance tests..."
        pytest "$PERFORMANCE_TESTS"
    fi
    ;;
  core)
    echo "Running core infrastructure tests..."
    check_directory "$CORE_TESTS" && pytest "$CORE_TESTS"
    ;;
  unit)
    echo "Running unit tests..."
    check_directory "$UNIT_TESTS" && pytest "$UNIT_TESTS"
    ;;
  integration)
    echo "Running integration tests..."
    check_directory "$INTEGRATION_TESTS" && pytest "$INTEGRATION_TESTS"
    ;;
  functional)
    echo "Running functional tests..."
    check_directory "$FUNCTIONAL_TESTS" && pytest "$FUNCTIONAL_TESTS"
    ;;
  performance)
    echo "Running performance tests..."
    check_directory "$PERFORMANCE_TESTS" && pytest "$PERFORMANCE_TESTS"
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
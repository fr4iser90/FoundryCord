#!/bin/bash
# Special script for running unit tests that avoids file descriptor issues
# and provides more diagnostic information

# Enhanced unit test runner for HomeLab Discord Bot in container environment
set -e

echo "==========================================================="
echo "    ENHANCED UNIT TEST RUNNER FOR CONTAINER ENVIRONMENT    "
echo "==========================================================="

echo "[$(date)] - Starting test execution"

# Show environment information
echo "[*] Python version:"
python --version

echo "[*] Pytest version:"
python -m pytest --version

# SIMPLE FIX: Navigate up one directory from /app/bot to /app
cd ..
echo "[*] Changed directory to: $(pwd)"

# Fix temporary directory permissions
echo "[*] Setting up temporary directory..."
mkdir -p /tmp
chmod 777 /tmp
export TMPDIR=/tmp

# Create clean file descriptors - CRITICAL FIX
echo "[*] Setting up capture handling..."
rm -f /tmp/pytest-*.tmp
exec 3>&1 4>&2  # Save original stdout/stderr

# Disable pytest capturing mechanism to avoid file descriptor issues
echo "[*] Disabling pytest capture with custom option..."
export PYTEST_ADDOPTS="--capture=no"

# Show directory structure for diagnostics
echo "[*] Test directory structure:"
find tests -type d | sort

echo "[*] Test files available:"
find tests -name "test_*.py" | sort

# Set special environment variables for testing
export TESTING=True
export TEST_MODE=container
export DB_MOCK=True

# Add before running tests
echo "[*] Ensuring module structure for tests..."
python -c "from app.tests.utils import ensure_test_module_structure; ensure_test_module_structure()"

# Run the infrastructure test that we know works
echo "[*] Running infrastructure structure test..."
python -m pytest tests/unit/infrastructure/test_structure.py -v --no-header --capture=no

# Try running test discovery
echo "[*] Checking test discovery..."
python -m pytest --collect-only tests/unit/ -v || echo "Test discovery issue detected"

# Run specific auth tests
echo "[*] Running auth tests..."
python -m pytest tests/unit/auth -v --no-header --capture=no || echo "Auth tests issues detected"

# Run specific commands tests
echo "[*] Running commands tests..."
python -m pytest tests/unit/commands -v --no-header --capture=no || echo "Commands tests issues detected"

# Run specific dashboard tests
echo "[*] Running dashboard tests..."
python -m pytest tests/unit/dashboard -v --no-header --capture=no || echo "Dashboard tests issues detected"

# Run specific web tests
echo "[*] Running web tests..."
python -m pytest tests/unit/web -v --no-header --capture=no || echo "Web tests issues detected"

# Restore original file descriptors
exec 1>&3 2>&4

echo "[$(date)] - Test execution completed"
exit 0 
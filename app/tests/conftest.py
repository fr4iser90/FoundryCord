"""
Global test configuration and fixtures for the HomeLab Discord Bot test suite.

This file contains:
1. Shared test fixtures used across multiple test types
2. Test categorization with pytest markers
3. Helper functions for test setup and teardown
"""
import pytest
import os
import sys

# ===== Test Categories =====
def pytest_configure(config):
    """Register custom markers to categorize tests."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as related to API functionality")
    config.addinivalue_line("markers", "dashboard: mark test as related to dashboard functionality")
    config.addinivalue_line("markers", "commands: mark test as related to Discord commands")
    config.addinivalue_line("markers", "slow: mark test as slow running")

# ===== Shared Fixtures =====
@pytest.fixture(scope="session")
def app_path():
    """Return the absolute path to the application directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def test_environment():
    """Set up the test environment and provide environment information."""
    # Print environment information for diagnostics
    print("\nPython version:", sys.version)
    print("Working directory:", os.getcwd())
    print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))
    
    # Set test environment variables
    os.environ['TESTING'] = 'True'
    
    yield "test"
    
    # Cleanup after all tests complete
    os.environ.pop('TESTING', None) 
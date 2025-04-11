"""
Global test configuration and fixtures for the HomeLab Discord Bot.
This file is automatically discovered by pytest.
"""
import os
import sys
import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
from app.tests.utils import (
    mock_db, 
    discord_bot, 
    web_request,
    mock_key_service,
    disable_db_logging,
    fix_container_tmpdir
)
import subprocess

# Add the project root to the Python path to make imports work correctly
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Disable SQLAlchemy logging for cleaner test output
disable_db_logging()

# Export fixtures for use in tests
__all__ = [
    'mock_db',
    'discord_bot',
    'web_request',
    'mock_key_service'
]

# ===== Test Categories =====
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Disable pytest capturing mechanisms to avoid file descriptor issues in containers."""
    if os.path.exists('/.dockerenv'):
        config.option.capture = "no"  # Disable capturing
        
        # Force create clean temporary directory
        if not os.path.exists('/tmp'):
            os.makedirs('/tmp', mode=0o777)
        else:
            os.chmod('/tmp', 0o777)

    """Register custom markers to categorize tests."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as related to API functionality")
    config.addinivalue_line("markers", "dashboard: mark test as related to dashboard functionality")
    config.addinivalue_line("markers", "commands: mark test as related to Discord commands")
    config.addinivalue_line("markers", "slow: mark test as slow running")

    # Check if fastapi is installed, if not install it
    try:
        import fastapi
    except ImportError:
        print("Installing fastapi for web tests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi"])
        


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

@pytest.fixture(scope="session")
def app_config():
    """Global test configuration fixture."""
    return {
        "test_mode": True,
        "database_url": os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:"),
    }

# Set up test database
@pytest.fixture(scope="session")
def db_session():
    """Create a fresh database session for testing."""
    from app.shared.infrastructure.models.config import get_session
    # Use a generator fixture to manage session lifecycle
    async def _get_test_session():
        async for session in get_session():
            yield session
            
    return _get_test_session

# Mock Discord bot for testing
@pytest.fixture
def mock_bot():
    """Create a mock Discord bot for testing."""
    bot = MagicMock()
    bot.user = MagicMock()
    bot.user.id = 12345
    return bot 

# Mock database session for unit tests
@pytest.fixture
def mock_db_session():
    """Provides a mock database session for unit tests"""
    mock_session = AsyncMock()
    
    # Create a mock result object that returns actual values
    mock_result = AsyncMock()
    mock_result.scalar = AsyncMock(return_value="test_value")
    mock_result.scalars = AsyncMock(return_value=mock_result)
    mock_result.all = AsyncMock(return_value=[])
    
    # Configure session methods to return our mock result
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock(return_value=True)
    mock_session.rollback = AsyncMock(return_value=True)
    mock_session.close = AsyncMock(return_value=True)
    mock_session.refresh = AsyncMock(return_value=True)
    
    return mock_session

# Mock get_session to return our mock session
@pytest.fixture
def mock_get_session(mock_db_session):
    """Patch the get_session function to return a mock session"""
    with patch('app.shared.infrastructure.database.models.config.get_session') as mock_get_session:
        async def mock_generator():
            yield mock_db_session
        mock_get_session.return_value = mock_generator()
        yield mock_db_session

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Save original environment
    original_env = {
        'APP_DB_USER': os.environ.get('APP_DB_USER'),
        'POSTGRES_HOST': os.environ.get('POSTGRES_HOST'),
        'POSTGRES_PORT': os.environ.get('POSTGRES_PORT'),
        'POSTGRES_DB': os.environ.get('POSTGRES_DB'),
        'APP_DB_PASSWORD': os.environ.get('APP_DB_PASSWORD'),
        'DATABASE_URL': os.environ.get('DATABASE_URL')
    }
    
    # Set test environment
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost:5432/test'
    os.environ['APP_DB_USER'] = 'test'
    os.environ['APP_DB_PASSWORD'] = 'test'
    os.environ['POSTGRES_HOST'] = 'localhost'
    os.environ['POSTGRES_PORT'] = '5432'
    os.environ['POSTGRES_DB'] = 'test'
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value 
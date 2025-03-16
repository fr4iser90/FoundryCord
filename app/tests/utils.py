"""
Test utilities for HomeLab Discord Bot.
Provides mocking helpers and test fixtures specifically designed for Docker environments.
"""
import os
import sys
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional, Callable, List, Union

# ===== Environment Configuration =====

# Detect if we're running in a container
IN_CONTAINER = os.path.exists('/.dockerenv')

# Set environment variables for testing
os.environ['TESTING'] = 'True'
os.environ['ENVIRONMENT'] = 'testing'

# Prevent actual database connections during tests
os.environ['DB_MOCK'] = 'True'

# ===== Database Mocking =====

def mock_db_session():
    """Create a mock database session that can be used in tests."""
    mock_session = AsyncMock()
    
    # Add common database methods
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    
    # Configure execute to return a mocked result proxy
    mock_result = AsyncMock()
    mock_result.scalar = AsyncMock(return_value=None)
    mock_result.scalars = AsyncMock()
    mock_result.scalars.return_value.first = AsyncMock(return_value=None)
    mock_result.scalars.return_value.all = AsyncMock(return_value=[])
    
    mock_session.execute.return_value = mock_result
    
    return mock_session

@pytest.fixture
async def mock_db():
    """Pytest fixture that patches the database session for testing."""
    # Path to patch depends on your application structure
    with patch('app.shared.infrastructure.database.models.config.get_session') as mock_get_session:
        # Setup mock session factory as an async generator
        async def mock_session_generator():
            session = mock_db_session()
            try:
                yield session
            finally:
                await session.close()
        
        # Configure the mock to yield our session
        mock_get_session.return_value = mock_session_generator()
        yield mock_get_session

# ===== Discord Mocking =====

def mock_discord_bot():
    """Create a mock Discord bot instance for testing."""
    mock_bot = MagicMock()
    
    # Setup common bot attributes
    mock_bot.user = MagicMock()
    mock_bot.user.id = 123456789
    mock_bot.user.name = "HomeLab Bot"
    
    # Setup common bot methods
    mock_bot.wait_until_ready = AsyncMock()
    mock_bot.get_channel = MagicMock(return_value=MagicMock())
    mock_bot.get_guild = MagicMock(return_value=MagicMock())
    
    # Setup components
    mock_bot.component_factory = MagicMock()
    mock_bot.component_factory.factories = {}
    
    # Setup services
    mock_bot.channel_config = MagicMock()
    mock_bot.channel_config.get_channel_id = AsyncMock(return_value=None)
    
    # For services that are async
    mock_bot.get_service = AsyncMock()
    
    return mock_bot

@pytest.fixture
def discord_bot():
    """Pytest fixture that provides a mocked Discord bot."""
    return mock_discord_bot()

# ===== Web/API Mocking =====

def mock_web_request(
    headers: Dict[str, str] = None,
    cookies: Dict[str, str] = None,
    query_params: Dict[str, str] = None,
    path_params: Dict[str, str] = None,
    json_data: Dict[str, Any] = None
):
    """Create a mock web request for testing API endpoints."""
    mock_request = MagicMock()
    
    # Setup request attributes
    mock_request.headers = headers or {}
    mock_request.cookies = cookies or {}
    mock_request.query_params = query_params or {}
    mock_request.path_params = path_params or {}
    
    # Setup async methods
    mock_request.json = AsyncMock(return_value=json_data or {})
    
    return mock_request

@pytest.fixture
def web_request():
    """Pytest fixture that provides a basic mocked web request."""
    return mock_web_request()

# ===== Key Services Mocking =====

@pytest.fixture
async def mock_key_service():
    """Mock the key management service used for encryption/JWT."""
    with patch('app.web.domain.auth.dependencies.get_key_management_service') as mock_kms:
        # Create our mock key manager
        mock_key_manager = AsyncMock()
        mock_key_manager.initialize = AsyncMock()
        mock_key_manager.get_jwt_secret_key = AsyncMock(return_value="test_secret_key")
        mock_key_manager.rotate_keys = AsyncMock()
        mock_key_manager.get_encryption_key = AsyncMock(return_value="test_encryption_key")
        
        # Return the mock when the service is requested
        mock_kms.return_value = mock_key_manager
        
        yield mock_key_manager

# ===== Test Helper Functions =====

def disable_db_logging():
    """Disable SQLAlchemy logging during tests."""
    import logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

def run_async(coroutine):
    """Run an async function in a synchronous context for testing."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)

# ===== Container-Specific Utilities =====

def fix_container_tmpdir():
    """
    Fix temporary directory issues in Docker container.
    This helps prevent "Bad file descriptor" errors with pytest.
    """
    if IN_CONTAINER:
        # Ensure clean temp dir
        import tempfile
        os.environ['TMPDIR'] = '/tmp'
        tempfile.tempdir = '/tmp'
        
        # Create directory if it doesn't exist and set permissions
        if not os.path.exists('/tmp'):
            os.makedirs('/tmp', mode=0o777)
        else:
            os.chmod('/tmp', 0o777)
            
        # Create a fresh temp file to verify permissions
        try:
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b'test')
            print("Temporary file access verified.")
        except Exception as e:
            print(f"Warning: Temporary file verification failed: {e}")

# Apply container fixes
fix_container_tmpdir()

def async_test(coro):
    """Decorator for running async test functions."""
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper

async def setup_test_guild():
    """Create a test guild with predefined channels and roles."""
    # Implementation here
    pass

def generate_fake_message(**kwargs):
    """Generate a fake Discord message for testing."""
    # Implementation here
    pass

# Add a helper function to check and create directory structures

def ensure_test_module_structure():
    """Ensures that all test directories have proper package structure."""
    import os
    
    # Create __init__.py files in test directories if they don't exist
    test_dirs = [
        "app/tests",
        "app/tests/unit",
        "app/tests/unit/auth",
        "app/tests/unit/commands",
        "app/tests/unit/dashboard",
        "app/tests/unit/infrastructure",
        "app/tests/unit/web",
        "app/tests/integration",
        "app/tests/functional",
        "app/tests/performance"
    ]
    bot_dir = [
        "app/bot"
    ]
    web_dir = [
        "app/web"
    ]
    
    for directory in test_dirs:
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
            
        # Create __init__.py if it doesn't exist
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# Test package\n")
            print(f"Created __init__.py in {directory}")
    
    print("Test module structure verified")
    return True 
"""Unit tests for KeyManagementService."""
import pytest
from datetime import datetime
import base64
import os
from unittest.mock import AsyncMock, MagicMock, patch
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.infrastructure.repositories.auth.key_repository_impl import KeyRepositoryImpl
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.session import SessionFactory

logger = get_db_logger()

@pytest.mark.unit
@pytest.mark.asyncio
class TestKeyManagementService:
    
    @pytest.fixture
    async def mock_session_factory(self):
        """Create a mock session factory."""
        mock_factory = MagicMock(spec=SessionFactory)
        mock_factory.initialized = True
        mock_factory.get_session = AsyncMock()
        return mock_factory
    
    @pytest.fixture
    async def mock_session(self, mock_session_factory):
        """Create a mock session."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session_factory.get_session.return_value = mock_session
        return mock_session
    
    @pytest.fixture
    async def key_repository(self, mock_session, mock_session_factory):
        """Create a KeyRepositoryImpl instance with a mock session."""
        with patch('app.shared.infrastructure.repositories.auth.key_repository_impl.SessionFactory', return_value=mock_session_factory):
            repository = KeyRepositoryImpl(mock_session)
            repository.session_factory = mock_session_factory
            
            # Configure mock methods with proper return values
            repository.get_jwt_secret_key = AsyncMock(return_value="test_jwt_secret")
            repository.get_encryption_key = AsyncMock(return_value=base64.urlsafe_b64encode(os.urandom(32)).decode())
            repository.get_encryption_keys = AsyncMock(return_value={
                'current_key': base64.urlsafe_b64encode(os.urandom(32)).decode(),
                'previous_key': base64.urlsafe_b64encode(os.urandom(32)).decode()
            })
            repository.save_encryption_keys = AsyncMock(return_value=True)
            repository.save_rotation_timestamp = AsyncMock(return_value=True)
            repository.save_jwt_secret_key = AsyncMock(return_value=True)
            repository.get_last_rotation_time = AsyncMock(return_value=datetime.now().isoformat())
            repository.store_key = AsyncMock(return_value=True)
            repository.initialize = AsyncMock(return_value=True)
            
            return repository
    
    @pytest.fixture
    async def key_service(self, key_repository, mock_session_factory):
        """Create a KeyManagementService instance with a mock repository."""
        with patch('app.shared.infrastructure.encryption.key_management_service.SessionFactory', return_value=mock_session_factory):
            service = KeyManagementService()
            service.key_repository = key_repository
            service.initialized = False  # Let initialization happen naturally
            return service
    
    async def test_initialization(self, key_service, key_repository):
        """Test service initialization."""
        # Test initialization
        result = await key_service.initialize()
        assert result is True
        assert key_service.initialized is True
        
        # Verify repository was called
        key_repository.get_jwt_secret_key.assert_awaited_once()
        key_repository.get_encryption_keys.assert_awaited_once()
    
    async def test_load_keys(self, key_service, key_repository):
        """Test loading keys from repository."""
        # Setup test keys
        test_current_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        test_previous_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock repository behavior
        key_repository.get_encryption_keys.return_value = {
            'current_key': test_current_key,
            'previous_key': test_previous_key
        }
        
        # Test loading keys
        result = await key_service._load_keys()
        assert result is True
        assert key_service.current_key == test_current_key
        assert key_service.previous_key == test_previous_key
        
        # Verify repository calls
        key_repository.get_encryption_keys.assert_awaited_once()
        key_repository.get_last_rotation_time.assert_awaited_once()
    
    async def test_key_rotation(self, key_service, key_repository):
        """Test key rotation functionality."""
        # Initialize service first
        await key_service.initialize()
        
        # Get initial keys
        initial_keys = await key_repository.get_encryption_keys()
        initial_current = initial_keys['current_key']
        
        # Test key rotation
        result = await key_service.rotate_keys()
        assert result is True
        
        # Verify keys were updated
        assert key_service.current_key != initial_current
        assert key_service.previous_key == initial_current
        
        # Verify repository calls
        key_repository.save_encryption_keys.assert_awaited_once()
        key_repository.save_rotation_timestamp.assert_awaited_once()
    
    async def test_needs_rotation(self, key_service, key_repository):
        """Test key rotation timing."""
        # Configure mock repository behavior
        key_repository.get_last_rotation_time.return_value = datetime.now().isoformat()
        
        # Test rotation timing
        needs_rotation = await key_service.needs_rotation()
        assert isinstance(needs_rotation, bool)
    
    async def test_get_jwt_secret_key(self, key_service, key_repository):
        """Test getting JWT secret key."""
        # Configure mock result
        test_jwt_secret = "test_jwt_secret"
        key_repository.get_jwt_secret_key.return_value = test_jwt_secret
        key_repository.get_encryption_key.return_value = None
        
        # Test getting JWT key
        jwt_key = await key_service.get_jwt_secret_key()
        assert jwt_key == test_jwt_secret
    
    async def test_get_encryption_key(self, key_service, key_repository):
        """Test getting encryption key."""
        # Configure mock result
        test_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        key_repository.get_jwt_secret_key.return_value = None
        key_repository.get_encryption_key.return_value = test_key
        
        # Test getting encryption key
        enc_key = await key_service.get_encryption_key()
        assert enc_key == test_key
    
    async def test_error_handling(self, key_service, key_repository):
        """Test error handling in key management operations."""
        # Configure mock to raise exceptions
        key_repository.get_jwt_secret_key.side_effect = Exception("Database error")
        key_repository.get_encryption_key.side_effect = Exception("Database error")
        
        # Test initialization error handling
        result = await key_service.initialize()
        assert result is False
        assert key_service.initialized is False 
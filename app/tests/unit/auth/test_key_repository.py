"""Unit tests for KeyRepositoryImpl."""
import pytest
from datetime import datetime
import base64
import os
from unittest.mock import AsyncMock, MagicMock, create_autospec
from app.shared.infrastructure.repositories.auth.key_repository_impl import KeyRepositoryImpl
from app.shared.interface.logging.api import get_db_logger
from sqlalchemy import text

logger = get_db_logger()

@pytest.mark.unit
@pytest.mark.asyncio
class TestKeyRepository:
    
    @pytest.fixture
    async def key_repository(self, mock_db_session):
        """Create a KeyRepositoryImpl instance with a mock session."""
        return KeyRepositoryImpl(mock_db_session)
    
    async def test_initialize(self, key_repository, mock_db_session):
        """Test repository initialization."""
        # Configure mock result
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test initialization
        result = await key_repository.initialize()
        assert result is True
        
        # Verify SQL execution
        assert mock_db_session.execute.called
        assert mock_db_session.commit.called
    
    async def test_store_and_get_key(self, key_repository, mock_db_session):
        """Test storing and retrieving a key."""
        test_key_name = "test_key"
        test_key_value = "test_value"
        
        # Configure mock result for key check and store
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test storing key
        store_result = await key_repository.store_key(test_key_name, test_key_value)
        assert store_result is True
        
        # Configure mock for key retrieval
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=test_key_value)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test retrieving key
        retrieved_key = await key_repository.get_key(test_key_name)
        assert retrieved_key == test_key_value
    
    async def test_get_encryption_keys(self, key_repository, mock_db_session):
        """Test getting encryption keys."""
        # Configure mock for current and previous keys
        current_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        previous_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock results for both keys
        mock_current_result = MagicMock()
        mock_current_result.scalar = AsyncMock(return_value=current_key)
        
        mock_previous_result = MagicMock()
        mock_previous_result.scalar = AsyncMock(return_value=previous_key)
        
        # Setup mock_db_session to return different results for different keys
        async def mock_execute(query, *args, **kwargs):
            query_str = str(query)
            if 'current_encryption_key' in query_str:
                return mock_current_result
            elif 'previous_encryption_key' in query_str:
                return mock_previous_result
            return MagicMock()
        
        mock_db_session.execute = AsyncMock(side_effect=mock_execute)
        
        # Test getting encryption keys
        keys = await key_repository.get_encryption_keys()
        assert isinstance(keys, dict), "Expected keys to be a dictionary"
        assert 'current_key' in keys, "Expected current_key in result"
        assert 'previous_key' in keys, "Expected previous_key in result"
        assert keys['current_key'] == current_key, "Current key mismatch"
        assert keys['previous_key'] == previous_key, "Previous key mismatch"
    
    async def test_save_encryption_keys(self, key_repository, mock_db_session):
        """Test saving encryption keys."""
        current_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        previous_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock result
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test saving keys
        result = await key_repository.save_encryption_keys(current_key, previous_key)
        assert result is True
        
        # Verify both keys were stored
        assert mock_db_session.execute.call_count >= 2
        assert mock_db_session.commit.called
    
    async def test_get_jwt_secret_key(self, key_repository, mock_db_session):
        """Test getting JWT secret key."""
        test_jwt_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock result
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=test_jwt_key)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test getting JWT key
        jwt_key = await key_repository.get_key('jwt_secret_key')
        assert jwt_key == test_jwt_key
    
    async def test_save_jwt_secret_key(self, key_repository, mock_db_session):
        """Test saving JWT secret key."""
        test_jwt_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock result
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test saving JWT key
        result = await key_repository.save_jwt_secret_key(test_jwt_key)
        assert result is True
        
        # Verify key was stored
        assert mock_db_session.execute.called
        assert mock_db_session.commit.called
    
    async def test_get_aes_key(self, key_repository, mock_db_session):
        """Test getting AES key."""
        test_aes_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock result
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=test_aes_key)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test getting AES key
        aes_key = await key_repository.get_key('aes_key')
        assert aes_key == test_aes_key
    
    async def test_save_aes_key(self, key_repository, mock_db_session):
        """Test saving AES key."""
        test_aes_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Configure mock result
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Test saving AES key
        result = await key_repository.save_aes_key(test_aes_key)
        assert result is True
        
        # Verify key was stored
        assert mock_db_session.execute.called
        assert mock_db_session.commit.called
    
    async def test_error_handling(self, key_repository, mock_db_session):
        """Test error handling in key operations."""
        # Configure mock to raise exceptions
        mock_db_session.execute = AsyncMock(side_effect=Exception("Database error"))
        
        # Test error handling in various operations
        assert await key_repository.get_key("test_key") is None
        assert await key_repository.store_key("test_key", "test_value") is False
        assert await key_repository.get_jwt_secret_key() is None
        assert await key_repository.save_jwt_secret_key("test_key") is False 
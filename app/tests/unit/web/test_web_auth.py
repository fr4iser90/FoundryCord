"""Unit tests for the web authentication functionality."""
import pytest
import jwt
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request

from app.web.domain.auth.dependencies import (
    WebAuthenticationService, 
    get_current_user,
    require_moderator
)

class TestWebAuthenticationService:
    """Tests for the WebAuthenticationService class."""
    
    @pytest.fixture
    def auth_service(self):
        """Create an authentication service for testing with mocked dependencies."""
        with patch('app.web.domain.auth.dependencies.get_key_management_service') as mock_kms:
            # Set up the mock KMS to return a predictable JWT secret
            mock_key_manager = AsyncMock()
            mock_key_manager.initialize = AsyncMock()
            mock_key_manager.get_jwt_secret_key = AsyncMock(return_value="test_secret_key")
            
            # Make the KMS factory return our mocked key manager
            mock_kms.return_value = lambda: mock_key_manager
            
            # Create the service
            service = WebAuthenticationService()
            return service
    
    @pytest.fixture
    async def initialized_auth_service(self, auth_service):
        """Return an initialized authentication service."""
        with patch('app.web.domain.auth.dependencies.get_db_connection') as mock_db_conn:
            # Mock database connection
            mock_db = AsyncMock()
            mock_db_conn.return_value = mock_db
            
            # Initialize the service
            await auth_service.initialize()
            return auth_service
    
    @pytest.mark.asyncio
    async def test_initialization(self, auth_service):
        """Test that the service initializes correctly."""
        with patch('app.web.domain.auth.dependencies.get_db_connection') as mock_db_conn:
            # Mock database connection
            mock_db = AsyncMock()
            mock_db_conn.return_value = mock_db
            
            # Initialize the service
            await auth_service.initialize()
            
            # Verify the service was initialized correctly
            assert auth_service._initialized is True
            assert auth_service.jwt_secret == "test_secret_key"
    
    @pytest.mark.asyncio
    async def test_initialization_error_handling(self, auth_service):
        """Test that initialization handles errors gracefully."""
        with patch('app.web.domain.auth.dependencies.get_db_connection') as mock_db_conn, \
             patch('app.web.domain.auth.dependencies.get_web_logger') as mock_logger, \
             patch.dict(os.environ, {"JWT_SECRET_KEY": "fallback_key"}):
            
            # Make the database connection raise an exception
            mock_db_conn.side_effect = Exception("Database connection failed")
            
            # Mock logger
            mock_logger.return_value = MagicMock()
            
            # Initialize the service
            await auth_service.initialize()
            
            # Verify error handling worked as expected
            assert auth_service._initialized is True
            assert auth_service.jwt_secret == "fallback_key"
            mock_logger.return_value.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_token_creation(self, initialized_auth_service):
        """Test creation of JWT access tokens."""
        # Create test data
        user_data = {
            "sub": "12345",
            "username": "test_user",
            "role": "ADMIN"
        }
        
        # Create a token
        token = initialized_auth_service.create_access_token(user_data)
        
        # Verify token is created correctly
        assert token is not None
        assert isinstance(token, str)
        
        # Decode the token to verify contents
        decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert decoded["sub"] == "12345"
        assert decoded["username"] == "test_user"
        assert decoded["role"] == "ADMIN"
        assert "exp" in decoded  # Check expiration is set
    
    @pytest.mark.asyncio
    async def test_token_validation_valid(self, initialized_auth_service):
        """Test validation of a valid token."""
        # Create a valid token with test data
        exp_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            "sub": "12345",
            "username": "test_user",
            "role": "ADMIN",
            "exp": exp_time
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        # Validate the token
        result = await initialized_auth_service.validate_token(token)
        
        # Verify the validation result
        assert result is not None
        assert result["id"] == "12345"
        assert result["username"] == "test_user"
        assert result["role"] == "ADMIN"
        assert result["authenticated"] is True
    
    @pytest.mark.asyncio
    async def test_token_validation_invalid(self, initialized_auth_service):
        """Test validation of an invalid token."""
        # Create an invalid token
        token = "invalid.token.format"
        
        # Validate the token
        result = await initialized_auth_service.validate_token(token)
        
        # Verify the validation result
        assert result is None
    
    @pytest.mark.asyncio
    async def test_token_validation_expired(self, initialized_auth_service):
        """Test validation of an expired token."""
        # Create an expired token
        exp_time = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": "12345",
            "username": "test_user",
            "role": "ADMIN",
            "exp": exp_time
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        # Validate the token
        result = await initialized_auth_service.validate_token(token)
        
        # Verify the validation result
        assert result is None


class TestAuthDependencies:
    """Tests for the authentication dependency functions."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock the global auth service for dependency injection testing."""
        with patch('app.web.domain.auth.dependencies.auth_service') as mock_service:
            mock_service.initialize = AsyncMock()
            mock_service.validate_token = AsyncMock()
            yield mock_service
    
    @pytest.mark.asyncio
    async def test_get_current_user_from_cookie(self, mock_auth_service):
        """Test extracting user from cookie."""
        # Set up mock
        mock_auth_service.validate_token.return_value = {
            "id": "12345",
            "username": "test_user",
            "role": "ADMIN",
            "authenticated": True
        }
        
        # Create mock request with cookie
        mock_request = MagicMock()
        mock_request.cookies = {"access_token": "test.token.value"}
        mock_request.headers = {}
        
        # Get current user
        user = await get_current_user(mock_request)
        
        # Verify
        assert user is not None
        assert user["id"] == "12345"
        assert user["role"] == "ADMIN"
        mock_auth_service.validate_token.assert_called_once_with("test.token.value")
    
    @pytest.mark.asyncio
    async def test_get_current_user_from_header(self, mock_auth_service):
        """Test extracting user from Authorization header."""
        # Set up mock
        mock_auth_service.validate_token.return_value = {
            "id": "12345",
            "username": "test_user",
            "role": "ADMIN",
            "authenticated": True
        }
        
        # Create mock request with Authorization header
        mock_request = MagicMock()
        mock_request.cookies = {}
        mock_request.headers = {"Authorization": "Bearer test.token.value"}
        
        # Get current user
        user = await get_current_user(mock_request)
        
        # Verify
        assert user is not None
        assert user["id"] == "12345"
        assert user["role"] == "ADMIN"
        mock_auth_service.validate_token.assert_called_once_with("test.token.value")
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, mock_auth_service):
        """Test behavior when no token is provided."""
        # Create mock request with no token
        mock_request = MagicMock()
        mock_request.cookies = {}
        mock_request.headers = {}
        
        # Get current user
        user = await get_current_user(mock_request)
        
        # Verify
        assert user is None
        mock_auth_service.validate_token.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_require_moderator_authorized(self):
        """Test moderator access check with sufficient permissions."""
        # Mock a user with admin privileges
        user = {
            "id": "12345",
            "username": "admin_user",
            "role": "ADMIN"
        }
        
        # Check permissions
        result = await require_moderator(user)
        
        # Verify
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_moderator_unauthorized(self):
        """Test moderator access check with insufficient permissions."""
        # Mock a user with insufficient privileges
        user = {
            "id": "12345",
            "username": "regular_user",
            "role": "USER"
        }
        
        # Check permissions - should raise an exception
        with pytest.raises(HTTPException) as excinfo:
            await require_moderator(user)
        
        # Verify exception
        assert excinfo.value.status_code == 403
        assert "Access denied" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_require_moderator_unauthenticated(self):
        """Test moderator access check with no user."""
        # No user (unauthenticated)
        user = None
        
        # Check permissions - should raise an exception
        with pytest.raises(HTTPException) as excinfo:
            await require_moderator(user)
        
        # Verify exception
        assert excinfo.value.status_code == 401
        assert "Authentication required" in excinfo.value.detail 
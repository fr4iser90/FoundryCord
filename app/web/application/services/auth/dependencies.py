from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from typing import Optional, Dict
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session.factory import get_session

# OAuth2 token URL and scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# JWT Algorithm
ALGORITHM = "HS256"

logger = get_web_logger()

# Global key service instance
_key_service = None

async def initialize_key_service():
    """Initialize the key service if not already initialized"""
    global _key_service
    if _key_service is None:
        _key_service = KeyManagementService()
        await _key_service.initialize()
    return _key_service

async def get_jwt_secret():
    """Get JWT secret key from key management service"""
    key_service = await initialize_key_service()
    return await key_service.get_jwt_secret_key()

async def get_current_user(request: Request):
    """Get the authenticated user or raise an exception (for API routes only)."""
    user = request.session.get("user")
    
    if not user:
        logger.warning("User not authenticated in API dependency")
        # For API calls, always return 401 Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return user

async def get_key_service() -> KeyManagementService:
    """Get the initialized key service"""
    return await initialize_key_service()

async def get_auth_service(key_service: KeyManagementService = Depends(get_key_service)) -> WebAuthenticationService:
    return WebAuthenticationService(key_service) 

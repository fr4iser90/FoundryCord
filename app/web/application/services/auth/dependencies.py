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
    """Get current user from session or raise an exception"""
    if not hasattr(request, "session"):
        logger.error("Session middleware not properly configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )
    
    user = request.session.get("user")
    
    # Debug user session
    logger.debug(f"Session contents: {request.session}")
    logger.debug(f"User from session: {user}")
    
    if not user:
        logger.warning("User not authenticated, redirecting to login")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_key_service() -> KeyManagementService:
    """Get the initialized key service"""
    return await initialize_key_service()

async def get_auth_service(key_service: KeyManagementService = Depends(get_key_service)) -> WebAuthenticationService:
    return WebAuthenticationService(key_service) 

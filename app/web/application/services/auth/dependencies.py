from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from typing import Optional, Dict
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService

# OAuth2 token URL and scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key_for_development_only")
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[Dict]:
    """
    Get the current authenticated user from the JWT token.
    Returns None if no valid token is provided.
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
            
        # Create a simple user object from JWT claims
        return {
            "id": user_id,
            "username": payload.get("username", "Unknown"),
            "authenticated": True
        }
    except JWTError:
        return None 
def get_key_service() -> KeyManagementService:
    return KeyManagementService()

def get_auth_service(key_service: KeyManagementService = Depends(get_key_service)) -> WebAuthenticationService:
    return WebAuthenticationService(key_service) 

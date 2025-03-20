from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
from jose import JWTError
import jwt as PyJWT
from datetime import datetime, timedelta
import logging
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService

logger = logging.getLogger("homelab.web")

# OAuth2 token URL and scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# Initialize constants
ALGORITHM = "HS256"

# Initialize auth service
class WebAuthenticationService:
    def __init__(self):
        self.key_manager = KeyManagementService()
        self.jwt_secret = None
        self._initialized = False

    async def initialize(self):
        """Async initialization"""
        if self._initialized:
            return
            
        try:
            # Initialisiere den KeyManagementService
            await self.key_manager.initialize()
            
            # Hole den JWT Key direkt mit await
            self.jwt_secret = await self.key_manager.get_jwt_secret_key()
                
            if not self.jwt_secret:
                raise Exception("Failed to get JWT secret key")
            
            self._initialized = True
            logger.info("WebAuthenticationService initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing WebAuthenticationService: {str(e)}")
            raise

    async def validate_token(self, token):
        """Validate a JWT token"""
        if not self._initialized:
            await self.initialize()
            
        try:
            payload = PyJWT.decode(token, self.jwt_secret, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
                
            return {
                "id": user_id,
                "username": payload.get("username", "Unknown"),
                "avatar": payload.get("avatar"),
                "role": payload.get("role", "GUEST"),
                "authenticated": True
            }
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def create_access_token(self, data: dict) -> str:
        """Create a new JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        encoded_jwt = PyJWT.encode(to_encode, self.jwt_secret, algorithm=ALGORITHM)
        return encoded_jwt

# Initialize global auth service
auth_service = WebAuthenticationService()

async def get_current_user(request: Request) -> Optional[Dict]:
    """Get the current authenticated user from the request"""
    try:
        # Initialize auth service if needed
        await auth_service.initialize()
        
        # Get token from cookie or header
        token = request.cookies.get("access_token")
        if not token:
            token = await oauth2_scheme(request)
            
        if not token:
            return None
            
        return await auth_service.validate_token(token)
        
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        return None

async def require_moderator(user = Depends(get_current_user)):
    """Dependency to require moderator role or higher"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_role = user.get("role", "GUEST")
    required_role = "SUPER_ADMIN"
    
    # Simple role hierarchy check
    role_levels = {
        "SUPER_ADMIN": 100,
        "ADMIN": 80,
        "MODERATOR": 60,
        "USER": 40,
        "GUEST": 20
    }
    
    if role_levels.get(user_role, 0) < role_levels.get(required_role, 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: requires {required_role} role or higher"
        )
    
    return user 
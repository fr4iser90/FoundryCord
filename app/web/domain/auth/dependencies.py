from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt as PyJWT
import os
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.infrastructure.encryption import get_key_management_service
from app.shared.infrastructure.database.management.connection import get_db_connection

# OAuth2 token URL and scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# Initialize constants
ALGORITHM = "HS256"

# Erstellen der Web Authentication Service Klasse (wie beim Bot)
class WebAuthenticationService:
    def __init__(self):
        KeyManagementService = get_key_management_service()
        self.key_manager = KeyManagementService()
        self.jwt_secret = None
        self._initialized = False

    async def initialize(self):
        """Async initialization"""
        if self._initialized:
            return
            
        try:
            # Erst die Datenbankverbindung holen
            db = await get_db_connection()
            # Dann den Key-Manager initialisieren
            await self.key_manager.initialize(db=db)
            # JWT secret key abrufen
            self.jwt_secret = await self.key_manager.get_jwt_secret_key()
            
            if not self.jwt_secret:
                logger.warning("JWT secret key not available! Using fallback secret")
                self.jwt_secret = os.getenv("JWT_SECRET_KEY", "fallback_secret_key")
            
            self._initialized = True
        except Exception as e:
            logger.error(f"Error initializing WebAuthenticationService: {e}")
            # Fallback zur Environment-Variable
            self.jwt_secret = os.getenv("JWT_SECRET_KEY", "fallback_secret_key")
            self._initialized = True

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

# Instanz erstellen (genau wie beim Bot)
auth_service = WebAuthenticationService()

async def get_current_user(request: Request) -> Optional[Dict]:
    """
    Get the current authenticated user from the JWT token.
    Returns None if no valid token is provided.
    """
    # Sicherstellen, dass der Service initialisiert ist
    await auth_service.initialize()
    
    # Token aus Cookie oder Header holen
    token = request.cookies.get("access_token")
    
    if not token and "Authorization" in request.headers:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    if not token or token == "Bearer None":
        return None
        
    # 'Bearer '-Präfix entfernen falls vorhanden
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
    
    # Token mit dem Service validieren
    return await auth_service.validate_token(token)

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
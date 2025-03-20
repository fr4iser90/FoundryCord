from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta

# Models
class Token(BaseModel):
    access_token: str
    token_type: str
    
class User(BaseModel):
    id: str
    username: str
    avatar: Optional[str] = None
    authenticated: bool = True

# Configuration
class AuthConfig:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", )
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    TOKEN_URL = "auth/token"

# OAuth2 token URL and scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AuthConfig.TOKEN_URL, auto_error=False)

def create_access_token(data: dict) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request) -> Optional[Dict]:
    """
    Get the current authenticated user from the JWT token.
    Returns None if no valid token is provided.
    """
    # Try to get token from cookie first
    token = request.cookies.get("access_token")
    
    # If not in cookie, try authorization header (for API calls)
    if not token and "Authorization" in request.headers:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    if not token or token == "Bearer None":
        return None
        
    # Remove 'Bearer ' prefix if it exists
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
        
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
            
        # Create a simple user object from JWT claims
        return {
            "id": user_id,
            "username": payload.get("username", "Unknown"),
            "avatar": payload.get("avatar"),
            "authenticated": True
        }
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None

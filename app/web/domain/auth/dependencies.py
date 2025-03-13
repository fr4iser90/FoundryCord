from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from typing import Optional, Dict

# OAuth2 token URL and scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key_for_development_only")
ALGORITHM = "HS256"

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
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    if not token or token == "Bearer None":
        return None
        
    # Remove 'Bearer ' prefix if it exists
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
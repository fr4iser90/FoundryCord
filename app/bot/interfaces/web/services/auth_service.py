import httpx
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from ..config import Settings
from ..models.user import User
import logging

settings = Settings()
logger = logging.getLogger("web_interface.auth_service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

class AuthService:
    """
    Service for handling authentication with Discord OAuth2
    """
    
    def get_oauth_url(self) -> str:
        """
        Generate the Discord OAuth2 authorization URL
        """
        params = {
            'client_id': settings.DISCORD_CLIENT_ID,
            'redirect_uri': settings.DISCORD_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'identify email',
        }
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"https://discord.com/api/oauth2/authorize?{query_string}"
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        data = {
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.DISCORD_REDIRECT_URI,
            'scope': 'identify email',
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://discord.com/api/oauth2/token',
                data=data,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                return {}
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Discord API
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://discord.com/api/users/@me',
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"User info request failed: {response.text}")
                return {}
            
            return response.json()
    
    async def create_or_update_user(self, user_info: Dict[str, Any]):
        """
        Create or update user in database
        """
        # This is a placeholder - in a real implementation, this would save to the database
        logger.info(f"Creating/updating user: {user_info['username']} ({user_info['id']})")
        
        # TODO: Implement database interaction
        return user_info
    
    async def generate_jwt(self, user_info: Dict[str, Any]) -> str:
        """
        Generate JWT token for user
        """
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user_info["id"]),
            "name": user_info["username"],
            "exp": expire
        }
        
        if "email" in user_info:
            to_encode["email"] = user_info["email"]
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    async def validate_jwt(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and return payload
        """
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.PyJWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

async def get_current_user(request: Request) -> User:
    """
    Get current user from JWT token in cookie
    """
    token = request.cookies.get("auth_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService()
    
    try:
        payload = await auth_service.validate_jwt(token)
        user = User(
            id=payload["sub"],
            username=payload["name"],
            email=payload.get("email", "")
        )
        return user
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
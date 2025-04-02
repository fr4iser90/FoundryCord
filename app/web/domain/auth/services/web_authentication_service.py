from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt
import os
from fastapi import HTTPException, status
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

class WebAuthenticationService:
    def __init__(self, key_service: KeyManagementService):
        self.key_service = key_service
        self.algorithm = "HS256"
        self.secret_key = os.getenv("JWT_SECRET_KEY", )
        logger.info("WebAuthenticationService initialized successfully")
        
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT access token
        
        Args:
            data: Dictionary containing claims to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
            
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
            
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Optional[Dict]: Decoded token claims if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.JWTError as e:
            logger.error(f"Error verifying token: {e}")
            return None

    def create_token(self, user_data: dict) -> str:
        try:
            secret_key = self.key_service.get_secret_key()
            # Token Erstellung mit dem Secret Key
            return "token"  # Hier kommt die eigentliche Token-Logik
        except Exception as e:
            logger.error(f"Failed to create token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create authentication token"
            )

    async def is_owner(self, user_id: str) -> bool:
        """Check if user is owner"""
        try:
            # Hier nur Web-spezifische Logik
            # Die eigentliche Rolle kommt aus der Session
            return True if user_id == "your_admin_id" else False
            
        except Exception as e:
            logger.error(f"Failed to check owner status: {e}")
            return False

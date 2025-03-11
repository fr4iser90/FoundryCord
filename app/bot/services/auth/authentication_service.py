from datetime import datetime, timedelta
import jwt as PyJWT
import os
from infrastructure.logging import logger
from infrastructure.security.key_management.key_manager import KeyManager

class AuthenticationService:
    def __init__(self, bot):
        self.bot = bot
        self.key_manager = KeyManager()
        self.jwt_secret = None
        self.session_duration = timedelta(hours=24)
        self.active_sessions = {}
        self.processed_requests = set()

    async def initialize(self):
        """Async initialization"""
        # Initialize key manager first
        await self.key_manager.initialize()
        # Now get JWT secret key
        self.jwt_secret = await self.key_manager.get_jwt_secret_key()
        
        if not self.jwt_secret:
            logger.warning("JWT secret key not available! Using fallback secret (not recommended for production)")
            self.jwt_secret = "fallback_secret_key"  # Only for development

    async def create_session(self, user_id):
        """Create a new session token"""
        expiry = datetime.utcnow() + self.session_duration
        token = PyJWT.encode({
            'user_id': str(user_id),
            'exp': expiry
        }, self.jwt_secret, algorithm='HS256')
        self.active_sessions[str(user_id)] = token
        return token

    async def validate_session(self, user_id, token):
        """Validate a session token"""
        try:
            if str(user_id) not in self.active_sessions:
                return False
            if self.active_sessions[str(user_id)] != token:
                return False
            payload = PyJWT.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload['user_id'] == str(user_id)
        except PyJWT.ExpiredSignatureError:
            del self.active_sessions[str(user_id)]
            return False
        except PyJWT.InvalidTokenError:
            return False

    async def revoke_session(self, user_id):
        """Revoke a user's session"""
        if str(user_id) in self.active_sessions:
            del self.active_sessions[str(user_id)]
            return True
        return False
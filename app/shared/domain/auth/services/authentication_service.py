from datetime import datetime, timedelta
import jwt as PyJWT
import os
from typing import Optional, Dict, Any
from app.shared.interfaces.logging.api import get_bot_logger
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity, SessionEntity
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl
from app.shared.infrastructure.database.service import DatabaseService
import httpx

logger = get_bot_logger()

class AuthenticationService:
    def __init__(self, key_service: KeyManagementService):
        self.key_service = key_service
        self.jwt_secret = None
        self.session_duration = timedelta(hours=24)
        self.active_sessions = {}
        self.processed_requests = set()
        self.db_service = DatabaseService()
        self.user_repository = None

    async def initialize(self):
        """Async initialization"""
        # Initialize key manager first
        await self.key_service.initialize()
        # Now get JWT secret key
        self.jwt_secret = await self.key_service.get_jwt_secret_key()
        
        if not self.jwt_secret:
            logger.warning("JWT secret key not available! Using fallback secret (NOT FOR PRODUCTION)")
            self.jwt_secret = "fallback_secret_key"  # Fallback for development/testing
            # We don't return here, allow initialization to continue with the fallback
        
        # Initialize database and repository
        await self.db_service.initialize()
        # Get session from database service
        session = await self.db_service.get_session()
        self.user_repository = UserRepositoryImpl(session)  # Pass session to repository

    async def create_session(self, user: AppUserEntity) -> str:
        """Create a new session token"""
        expiry = datetime.utcnow() + self.session_duration
        token = PyJWT.encode({
            'user_id': str(user.id),
            'exp': expiry
        }, self.jwt_secret, algorithm='HS256')
        
        # Create session entity
        session = SessionEntity(
            user_id=user.id,
            token=token,
            expires_at=expiry
        )
        user.sessions.append(session)
        
        # Store in memory for quick validation
        self.active_sessions[str(user.id)] = token
        return token

    async def validate_session(self, user_id: str, token: str) -> bool:
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

    async def revoke_session(self, user_id: str) -> bool:
        """Revoke a user's session"""
        if str(user_id) in self.active_sessions:
            del self.active_sessions[str(user_id)]
            return True
        return False

    async def create_access_token(self, user: AppUserEntity) -> str:
        """Create JWT token"""
        expiry = datetime.utcnow() + self.session_duration
        
        # Get role from guild_roles if available
        role_name = "GUEST"
        if user.is_owner:
            role_name = "OWNER"
        elif user.guild_roles:
            role_name = user.guild_roles[0].role.name
        
        token_data = {
            'sub': str(user.id),
            'username': user.username,
            'is_owner': user.is_owner,
            'role': role_name,
            'exp': expiry
        }
        return PyJWT.encode(token_data, self.jwt_secret, algorithm='HS256')

    async def validate_token(self, token: str) -> Optional[AppUserEntity]:
        """Validate JWT and return User"""
        try:
            payload = PyJWT.decode(token, self.jwt_secret, algorithms=['HS256'])
            return await self.user_repository.get_by_id(payload['sub'])
        except PyJWT.InvalidTokenError:
            return None

    async def handle_oauth_callback(self, code: str) -> Optional[Dict[str, Any]]:
        """Handle OAuth callback from Discord"""
        try:
            # Ensure repository is initialized
            if not self.user_repository:
                await self.initialize()
                
            # Get Discord OAuth config
            client_id = os.getenv("DISCORD_BOT_ID")
            client_secret = os.getenv("DISCORD_BOT_SECRET")
            redirect_uri = os.getenv("DISCORD_REDIREST_URI", "http://localhost:8000/auth/callback")

            # Validate config
            if not client_id or not client_secret:
                logger.error(f"Missing Discord OAuth config: ID={bool(client_id)}, Secret={bool(client_secret)}")
                raise Exception("Discord OAuth configuration is incomplete")

            # Exchange code for token
            token_url = "https://discord.com/api/oauth2/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "scope": "identify guilds"
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with httpx.AsyncClient() as client:
                # Get token
                token_response = await client.post(
                    token_url, 
                    data=data,
                    headers=headers
                )
                
                if token_response.status_code != 200:
                    logger.error(f"Token request failed: {token_response.text}")
                    raise Exception(f"Token request failed: {token_response.status_code}")
                    
                token_data = token_response.json()
                if "access_token" not in token_data:
                    logger.error(f"No access token in response: {token_data}")
                    raise Exception("No access token in response")
                    
                access_token = token_data["access_token"]
                
                # Get user info
                headers = {"Authorization": f"Bearer {access_token}"}
                user_response = await client.get("https://discord.com/api/users/@me", headers=headers)
                
                if user_response.status_code != 200:
                    logger.error(f"User info request failed: {user_response.text}")
                    raise Exception(f"User info request failed: {user_response.status_code}")
                    
                user_data = user_response.json()
                
                # Check if user exists in database
                user = await self.user_repository.get_by_discord_id(str(user_data["id"]))
                
                if not user:
                    logger.warning(f"User {user_data['id']} not found in database")
                    return None
                
                # Owner hat immer Zugang
                if user.is_owner:
                    return {
                        "id": user.id,
                        "username": user.username,
                        "discord_id": user.discord_id,
                        "is_owner": True,
                        "avatar": user.avatar
                    }
                
                # Get user's guilds
                guilds_response = await client.get("https://discord.com/api/users/@me/guilds", headers=headers)
                if guilds_response.status_code != 200:
                    logger.error(f"Guilds request failed: {guilds_response.text}")
                    raise Exception(f"Guilds request failed: {guilds_response.status_code}")
                    
                guilds_data = guilds_response.json()
                
                # Check if user is in any approved guild
                approved_guild = None
                guild_role = None
                for guild in guilds_data:
                    role = await self.user_repository.get_user_role_in_guild(str(user_data["id"]), guild["id"])
                    if role:
                        approved_guild = guild
                        guild_role = role
                        break
                
                if not approved_guild:
                    logger.warning(f"User {user_data['id']} not in any approved guild")
                    return None
                
                # Return user data with guild role
                return {
                    "id": user.id,
                    "username": user.username,
                    "discord_id": user.discord_id,
                    "is_owner": False,
                    "guild_id": approved_guild["id"],
                    "guild_name": approved_guild["name"],
                    "role": guild_role,
                    "avatar": user.avatar
                }
                
        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            raise
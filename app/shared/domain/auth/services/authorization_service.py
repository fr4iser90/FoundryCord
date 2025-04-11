from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.policies import is_authorized
from typing import Optional

logger = get_bot_logger()

class AuthorizationService:
    def __init__(self, bot):
        self.bot = bot

    async def check_authorization(self, user: AppUserEntity) -> bool:
        """Check if a user is authorized"""
        sanitized_user = f"User_{hash(str(user.id))}"
        logger.debug(f"Authorization check for user: {sanitized_user}")
        
        # Owner is always authorized
        if user.is_owner:
            return True
            
        # Check if user has any guild roles
        if not user.guild_roles:
            return False
            
        # Check if any guild role is active
        return any(
            guild_user.role is not None 
            for guild_user in user.guild_roles
        )

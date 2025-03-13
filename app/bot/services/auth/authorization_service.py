from app.shared.logging import logger
from app.bot.domain.auth.models import User, Role, Permission
from app.bot.domain.auth.policies import is_authorized
# OR if you moved to domain services:
# from app.bot.domain.auth.services.permission_service import PermissionService

class AuthorizationService:
    def __init__(self, bot):
        self.bot = bot
        # If using domain service approach:
        # self.permission_service = PermissionService()

    async def check_authorization(self, user):
        """Check if a user is authorized"""
        sanitized_user = f"User_{hash(str(user.id))}"
        logger.debug(f"Authorization check for user: {sanitized_user}")
        return is_authorized(user)
        # OR with domain service:
        # return self.permission_service.is_authorized(user)
        
    # Add more specific permission checks here as needed
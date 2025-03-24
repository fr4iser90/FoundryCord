from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.domain.auth.models import User, Role, Permission
from app.shared.domain.auth.policies import is_authorized


class AuthorizationService:
    def __init__(self, bot):
        self.bot = bot


    async def check_authorization(self, user):
        """Check if a user is authorized"""
        sanitized_user = f"User_{hash(str(user.id))}"
        logger.debug(f"Authorization check for user: {sanitized_user}")
        return is_authorized(user)

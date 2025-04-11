# app/bot/services/auth/__init__.py
from app.shared.domain.auth.services import AuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService

__all__ = [
    'AuthenticationService',
]

# Initialize services
key_service = KeyManagementService()
auth_service = AuthenticationService(key_service)

## You can now use:
#from app.bot.core.services.auth import AuthenticationService, AuthorizationService
from .permission_service import PermissionService
from .authentication_service import AuthenticationService
from .authorization_service import AuthorizationService

__all__ = [
    'PermissionService',
    'AuthenticationService',
    'AuthorizationService',
    'setup'
]

async def setup(bot):
    """Central initialization of the Authentication and Authorization services"""
    try:
        # Initialize authentication service
        auth_service = AuthenticationService(bot)
        await auth_service.initialize()
        bot.authentication = auth_service
        
        # Initialize authorization service
        authorization_service = AuthorizationService(bot)
        bot.authorization = authorization_service
        
        return {
            'authentication': auth_service,
            'authorization': authorization_service
        }
    except Exception as e:
        raise
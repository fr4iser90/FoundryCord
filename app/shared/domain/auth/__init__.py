from app.shared.domain.auth.models import User, Role, Permission
from app.shared.domain.auth.models import OWNER, ADMINS, MODERATORS, USERS, GUESTS, SERVER_ROLES
from app.shared.domain.auth.policies import is_bot_owner, is_admin, is_moderator, is_user, is_guest, is_authorized
from app.shared.domain.auth.services import PermissionService, AuthorizationService, AuthenticationService

__all__ = [
    # Models
    'User', 'Role', 'Permission',
    'SERVER_ROLES',
    'OWNER', 'ADMINS', 'MODERATORS', 'USERS', 'GUESTS',
    
    # Policy functions
    'is_bot_owner', 'is_admin', 'is_moderator', 
    'is_user', 'is_guest', 'is_authorized',
    
    # Services
    'PermissionService',
    'AuthorizationService',
    'AuthenticationService'
] 

# # If you need everything
# from app.shared.domain.auth import User, Role, Permission, is_authorized

# # If you need just models
# from app.shared.domain.auth.models import User, Role, Permission

# # If you need just policies
# from app.shared.domain.auth.policies import is_authorized

# # If you need the permission service
# from app.shared.domain.auth.services import PermissionService
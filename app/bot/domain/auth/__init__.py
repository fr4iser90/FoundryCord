from .models import User, Role, Permission
from .models import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS, SERVER_ROLES
from .policies import is_super_admin, is_admin, is_moderator, is_user, is_guest, is_authorized
from .services import PermissionService

__all__ = [
    # Models
    'User', 'Role', 'Permission',
    'SERVER_ROLES',
    'SUPER_ADMINS', 'ADMINS', 'MODERATORS', 'USERS', 'GUESTS',
    
    # Policy functions
    'is_super_admin', 'is_admin', 'is_moderator', 
    'is_user', 'is_guest', 'is_authorized',
    
    # Services
    'PermissionService'
] 


# # If you need everything
# from domain.auth import User, Role, Permission, is_authorized

# # If you need just models
# from domain.auth.models import User, Role, Permission

# # If you need just policies
# from domain.auth.policies import is_authorized

# # If you need the permission service
# from domain.auth.services import PermissionService
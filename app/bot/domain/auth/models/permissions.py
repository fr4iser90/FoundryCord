from enum import Enum, auto
from app.bot.infrastructure.logging import logger
from .roles import Role, SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS

class Permission(Enum):
    """Specific permissions for actions in the system"""
    VIEW_SYSTEM_STATUS = auto()
    MANAGE_USERS = auto()
    RESTART_SERVICES = auto()
    VIEW_LOGS = auto()
    MANAGE_BACKUPS = auto()
    EXECUTE_COMMANDS = auto()
    # Add more as needed
    
    @staticmethod
    def get_role_permissions(role):
        """Get all permissions for a specific role"""
        if role == Role.SUPER_ADMIN:
            return list(Permission)
            
        if role == Role.ADMIN:
            return [p for p in Permission if p != Permission.MANAGE_USERS]
            
        if role == Role.MODERATOR:
            return [
                Permission.VIEW_SYSTEM_STATUS,
                Permission.VIEW_LOGS,
                Permission.RESTART_SERVICES
            ]
            
        if role == Role.USER:
            return [Permission.VIEW_SYSTEM_STATUS]
            
        # GUEST role
        return []

def is_super_admin(user):
    """Check if the user is a Super Admin."""
    return str(user.id) in SUPER_ADMINS.values()

def is_admin(user):
    """Check if the user is an Admin or Super Admin."""
    return is_super_admin(user) or str(user.id) in ADMINS.values()

def is_moderator(user):
    """Check if the user is a Moderator or higher."""
    return is_admin(user) or str(user.id) in MODERATORS.values()

def is_user(user):
    """Check if the user is a regular User or higher."""
    return is_moderator(user) or str(user.id) in USERS.values()

def is_guest(user):
    """Check if the user is a Guest or higher."""
    return str(user.id) in GUESTS.values()

def is_authorized(user):
    """Check if the user is authorized."""
    user_id = str(user.id)
    # Use debug level instead of print for role checks
    logger.debug(f"Authorization check for user ID: {user_id}")
    
    # Remove sensitive data from logs
    roles_present = {
        'super_admin': bool(SUPER_ADMINS),
        'admin': bool(ADMINS),
        'moderator': bool(MODERATORS),
        'user': bool(USERS),
        'guest': bool(GUESTS)
    }
    logger.debug(f"Available roles: {roles_present}")
    
    return (
        is_super_admin(user)
        or is_admin(user)
        or is_moderator(user)
        or is_user(user)
        or is_guest(user)
    )

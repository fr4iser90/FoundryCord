from core.services.logging.logging_commands import logger
from .users import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS

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
# modules/auth/permissions.py

try:
    from core.config.users import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
except ImportError:
    # Fallback if config cannot be imported
    SUPER_ADMINS = {}
    ADMINS = {}
    MODERATORS = {}
    USERS = {}
    GUESTS = {}

def is_super_admin(user):
    """Check if the user is a Super Admin."""
    return str(user.id) in SUPER_ADMINS

def is_admin(user):
    """Check if the user is an Admin or Super Admin."""
    return is_super_admin(user) or str(user.id) in ADMINS

def is_moderator(user):
    """Check if the user is a Moderator or higher."""
    return is_admin(user) or str(user.id) in MODERATORS

def is_user(user):
    """Check if the user is a regular User or higher."""
    return is_moderator(user) or str(user.id) in USERS

def is_guest(user):
    """Check if the user is a Guest or higher."""
    return str(user.id) in GUESTS

def is_authorized(user, required_roles):
    """Check if the user has any of the required roles or higher."""
    role_checks = {
        "SUPER_ADMIN": is_super_admin,
        "ADMIN": is_admin,
        "MODERATOR": is_moderator,
        "USER": is_user,
        "GUEST": is_guest
    }

    for role in required_roles:
        if role_checks.get(role, lambda user: False)(user):
            return True
    return False

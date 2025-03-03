# modules/auth/permissions.py
from config.users import ADMINS, GUESTS, DEV_ROLES

def is_super_admin(user):
    """Check if the user is a Super Admin."""
    return str(user.id) in ADMINS["SUPER_ADMIN"]

def is_admin(user):
    """Check if the user is an Admin or Super Admin."""
    return is_super_admin(user) or str(user.id) in ADMINS["ADMIN"]

def is_moderator(user):
    """Check if the user is a Moderator or higher."""
    return is_admin(user) or str(user.id) in ADMINS["MODERATOR"]

def is_dev(user):
    """Check if the user is a Developer or higher."""
    return is_admin(user) or str(user.id) in DEV_ROLES

def is_guest(user):
    """Check if the user is a Guest or higher."""
    return str(user.id) in GUESTS["GUEST"]

def is_authorized(user, required_roles):
    """Check if the user has any of the required roles or higher."""
    role_checks = {
        "SUPER_ADMIN": is_super_admin,
        "ADMIN": is_admin,
        "MODERATOR": is_moderator,
        "DEV": is_dev,
        "GUEST": is_guest
    }
    
    for role in required_roles:
        if role_checks.get(role, lambda user: False)(user):
            return True
    return False

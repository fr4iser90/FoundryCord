# modules/auth/permissions.py

try:
    from core.config.users import SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
except ImportError as e:
    print(f"Error importing user roles: {e}")
    # Fallback if config cannot be imported
    SUPER_ADMINS = {}
    ADMINS = {}
    MODERATORS = {}
    USERS = {}
    GUESTS = {}

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
    """
    Überprüft, ob der Benutzer in einer der Listen (SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS) enthalten ist.
    """
    user_id = str(user.id)
    print(f"Checking authorization for user ID: {user_id}")  # Debugging
    print(f"SUPER_ADMINS: {SUPER_ADMINS}")  # Debugging
    print(f"ADMINS: {ADMINS}")  # Debugging
    print(f"MODERATORS: {MODERATORS}")  # Debugging
    print(f"USERS: {USERS}")  # Debugging
    print(f"GUESTS: {GUESTS}")  # Debugging
    return (
        is_super_admin(user)
        or is_admin(user)
        or is_moderator(user)
        or is_user(user)
        or is_guest(user)
    )
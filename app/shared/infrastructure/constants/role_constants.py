"""Constants related to app_roles and permissions in the system"""

# Server role configuration
SERVER_ROLES = {
    "OWNER": ["Bot Owner"],  # Full, unrestricted access
    "ADMIN": ["Admin"],  # High-level control, but some restrictions
    "MODERATOR": ["Moderator"],  # Moderates content, but limited system access
    "USER": ["User"],  # Basic user, limited access
    "GUEST": ["Guest"],  # View-only access
}

# Role priorities (higher number = higher privilege)
ROLE_PRIORITIES = {
    "OWNER": 100,
    "ADMIN": 80,
    "MODERATOR": 60,
    "USER": 40,
    "GUEST": 20
}

# Default user groups - will be filled from environment variables at runtime
DEFAULT_USER_GROUPS = {
    'owner': {},
    'admins': {},
    'moderators': {},
    'users': {},
    'guests': {}
}
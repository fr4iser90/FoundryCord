"""User role group constants"""
from enum import Enum
from app.shared.infrastructure.database.config.user_config import load_user_groups

class UserRole(Enum):
    """User role enumeration"""
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

# Load user groups at import time (behalten wir bei)
USER_GROUPS = load_user_groups()
OWNER = USER_GROUPS['OWNER']
ADMINS = USER_GROUPS['admins']
MODERATORS = USER_GROUPS['moderators']
USERS = USER_GROUPS['users']
GUESTS = USER_GROUPS['guests']

# Role descriptions für die Migration
ROLE_DESCRIPTIONS = {
    UserRole.OWNER.value: "Bot owner with full system access and control",
    UserRole.ADMIN.value: "Administrator with elevated privileges and management access",
    UserRole.MODERATOR.value: "Moderator with channel and user management capabilities",
    UserRole.USER.value: "Regular user with standard access",
    UserRole.GUEST.value: "Guest user with limited access"
}
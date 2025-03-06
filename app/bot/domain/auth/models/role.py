from enum import Enum
from typing import Dict, List, Optional
from infrastructure.config.env_loader import load_user_groups

# Server role configuration - stays in domain because it's core business logic
SERVER_ROLES = {
    "SUPER_ADMIN": ["Super Admin"],  # Full, unrestricted access
    "ADMIN": ["Admin"],  # High-level control, but some restrictions
    "MODERATOR": ["Moderator"],  # Moderates content, but limited system access
    "USER": ["User"],  # Basic user, limited access
    "GUEST": ["Guest"],  # View-only access
}

# Load user groups from environment
user_groups = load_user_groups()
SUPER_ADMINS = user_groups['super_admins']
ADMINS = user_groups['admins']
MODERATORS = user_groups['moderators']
USERS = user_groups['users']
GUESTS = user_groups['guests']

class Role(Enum):
    """Value object representing user roles in the system"""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"
    GUEST = "GUEST"
    
    @property
    def priority(self) -> int:
        """Return role priority (higher number = higher privilege)"""
        priorities = {
            Role.SUPER_ADMIN: 100,
            Role.ADMIN: 80,
            Role.MODERATOR: 60,
            Role.USER: 40,
            Role.GUEST: 20
        }
        return priorities.get(self, 0)
        
    def can_access(self, required_role) -> bool:
        """Check if this role has access to features requiring the given role"""
        return self.priority >= required_role.priority
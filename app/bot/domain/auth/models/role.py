from enum import Enum
from typing import Dict, List, Optional
from infrastructure.config.constants.role_constants import SERVER_ROLES, ROLE_PRIORITIES
# Importiere Benutzergruppen aus der Constants-Datei 
from infrastructure.config.constants.user_groups import (
    SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
)

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
        return ROLE_PRIORITIES.get(self.value, 0)
        
    def can_access(self, required_role) -> bool:
        """Check if this role has access to features requiring the given role"""
        return self.priority >= required_role.priority
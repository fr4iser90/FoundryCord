from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .role import Role
from .permission import Permission

@dataclass
class User:
    id: str
    username: str
    role: Role
    created_at: datetime = None
    last_active: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in Permission.get_role_permissions(self.role)
        
    def can_access(self, required_role: Role) -> bool:
        """Check if user can access features requiring the given role"""
        return self.role.can_access(required_role)
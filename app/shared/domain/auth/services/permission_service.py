from app.shared.domain.auth.policies import (
    is_authorized, is_bot_owner, is_admin, 
    is_moderator, is_user, is_guest
)
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from typing import Optional, List

class PermissionService:
    """Domain service for permission-related operations"""
    
    def is_authorized(self, user: AppUserEntity) -> bool:
        """Check if a user is authorized to use the system"""
        if user.is_owner:
            return True
        return bool(user.guild_roles)  # User has at least one guild role
    
    def is_bot_owner(self, user: AppUserEntity) -> bool:
        """Check if user is a Super Admin"""
        return user.is_owner
        
    def is_admin(self, user: AppUserEntity) -> bool:
        """Check if user is an Admin"""
        if user.is_owner:
            return True
        return any(guild_user.role.name == "ADMIN" for guild_user in user.guild_roles)
        
    def is_moderator(self, user: AppUserEntity) -> bool:
        """Check if user is a Moderator or higher"""
        if user.is_owner:
            return True
        return any(guild_user.role.name in ["ADMIN", "MODERATOR"] for guild_user in user.guild_roles)
        
    def is_user(self, user: AppUserEntity) -> bool:
        """Check if user is a regular User or higher"""
        if user.is_owner:
            return True
        return any(guild_user.role.name in ["ADMIN", "MODERATOR", "USER"] for guild_user in user.guild_roles)
        
    def is_guest(self, user: AppUserEntity) -> bool:
        """Check if user is a Guest or higher"""
        if user.is_owner:
            return True
        return bool(user.guild_roles)  # Any role counts as at least guest
        
    def get_permissions(self, user: AppUserEntity) -> List[str]:
        """Get all permissions for a user"""
        if user.is_owner:
            return ["*"]  # Owner has all permissions
        if not user.guild_roles:
            return []
        # Get permissions from first guild role
        role = user.guild_roles[0].role
        return role.permissions.split(",") if role.permissions else []
        
    def has_permission(self, user: AppUserEntity, permission: str) -> bool:
        """Check if user has a specific permission"""
        if user.is_owner:
            return True
        permissions = self.get_permissions(user)
        return permission in permissions or "*" in permissions

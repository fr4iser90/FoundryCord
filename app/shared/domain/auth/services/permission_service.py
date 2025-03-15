from ..policies.authorization_policies import (
    is_authorized, is_super_admin, is_admin, 
    is_moderator, is_user, is_guest
)
from app.shared.domain.auth.models import Permission

class PermissionService:
    """Domain service for permission-related operations"""
    
    def is_authorized(self, user):
        """Check if a user is authorized to use the system"""
        return is_authorized(user)
    
    def is_super_admin(self, user):
        """Check if user is a Super Admin"""
        return is_super_admin(user)
        
    def is_admin(self, user):
        """Check if user is an Admin or Super Admin"""
        return is_admin(user)
        
    def is_moderator(self, user):
        """Check if user is a Moderator or higher"""
        return is_moderator(user)
        
    def is_user(self, user):
        """Check if user is a regular User or higher"""
        return is_user(user)
        
    def is_guest(self, user):
        """Check if user is a Guest or higher"""
        return is_guest(user)
        
    def has_permission(self, user, permission):
        """Check if user has a specific permission"""
        return permission in Permission.get_role_permissions(user.role)

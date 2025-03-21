from enum import Enum, auto
from .role import Role

class Permission(Enum):
    """Value object for specific permissions for actions in the system"""
    VIEW_SYSTEM_STATUS = auto()
    MANAGE_USERS = auto()
    RESTART_SERVICES = auto()
    VIEW_LOGS = auto()
    MANAGE_BACKUPS = auto()
    EXECUTE_COMMANDS = auto()
    # Add more as needed
    
    @staticmethod
    def get_role_permissions(role):
        """Get all permissions for a specific role"""
        if role == Role.OWNER:
            return list(Permission)
            
        if role == Role.ADMIN:
            return [p for p in Permission if p != Permission.MANAGE_USERS]
            
        if role == Role.MODERATOR:
            return [
                Permission.VIEW_SYSTEM_STATUS,
                Permission.VIEW_LOGS,
                Permission.RESTART_SERVICES
            ]
            
        if role == Role.USER:
            return [Permission.VIEW_SYSTEM_STATUS]
            
        # GUEST role
        return []

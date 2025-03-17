from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class CategoryPermissionLevel(Enum):
    """Permission levels for categories in Discord"""
    PUBLIC = "public"
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class CategoryPermission:
    """Represents permissions for a specific role within a category"""
    role_id: int
    view: bool = False
    send_messages: bool = False
    manage_messages: bool = False
    manage_channels: bool = False
    manage_category: bool = False


@dataclass
class CategoryModel:
    """Domain model representing a Discord category"""
    id: Optional[int] = None  # Database ID
    discord_id: Optional[int] = None  # Discord category ID
    name: str = ""
    position: int = 0
    permission_level: CategoryPermissionLevel = CategoryPermissionLevel.PUBLIC
    permissions: List[CategoryPermission] = None
    is_enabled: bool = True
    is_created: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.metadata is None:
            self.metadata = {}
            
    @property
    def is_valid(self) -> bool:
        """Validate if category has all required information"""
        return bool(self.name and self.position >= 0)


@dataclass
class CategoryTemplate:
    """Template for creating categories with predefined configurations"""
    name: str
    position: int
    permission_level: CategoryPermissionLevel
    permissions: List[CategoryPermission]
    metadata: Dict[str, Any]
    is_enabled: bool = True
    
    def to_category_model(self) -> CategoryModel:
        """Convert template to a CategoryModel instance"""
        return CategoryModel(
            name=self.name,
            position=self.position,
            permission_level=self.permission_level,
            permissions=self.permissions.copy(),
            is_enabled=self.is_enabled,
            metadata=self.metadata.copy()
        ) 
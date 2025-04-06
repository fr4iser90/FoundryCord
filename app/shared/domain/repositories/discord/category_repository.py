from abc import ABC, abstractmethod
from typing import Optional, List, Any
from app.shared.infrastructure.models.discord.entities.category_entity import CategoryEntity
from app.shared.infrastructure.models.discord.mappings.category_mapping import CategoryMapping

class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: int) -> Optional[CategoryEntity]:
        pass
    
    @abstractmethod
    async def get_by_discord_id(self, category_discord_id: str) -> Optional[CategoryEntity]:
        pass
    
    @abstractmethod
    async def get_by_guild_and_type(self, guild_id: str, category_type: str) -> Optional[CategoryMapping]:
        pass
    
    @abstractmethod
    async def get_by_type(self, category_type: str) -> Optional[CategoryMapping]:
        pass
    
    @abstractmethod
    async def get_by_guild(self, guild_id: str) -> List[CategoryMapping]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[CategoryEntity]:
        pass
    
    @abstractmethod
    async def create(self, guild_id: str, category_id: str, category_name: str, category_type: str = "homelab") -> CategoryMapping:
        pass
    
    @abstractmethod
    async def update(self, category: CategoryEntity) -> CategoryEntity:
        pass
    
    @abstractmethod
    async def delete(self, category: CategoryEntity) -> None:
        pass
    
    @abstractmethod
    async def save_or_update(self, guild_id: str, category_id: str, category_name: str, category_type: str) -> CategoryMapping:
        pass
    
    @abstractmethod
    async def get_all_categories(self) -> List[CategoryEntity]:
        """Get all categories"""
        pass
    
    @abstractmethod
    async def get_enabled_categories(self) -> List[CategoryEntity]:
        """Get all enabled categories"""
        pass
    
    @abstractmethod
    async def update_discord_id(self, category_id: int, discord_id: str) -> None:
        """Update the Discord ID for a category"""
        pass
    
    @abstractmethod
    async def update_category_status(self, category_id: int, created: bool) -> None:
        """Update the created status for a category"""
        pass
    
    @abstractmethod
    async def update_position(self, category_id: int, position: int) -> None:
        """Update the position for a category"""
        pass
    
    @abstractmethod
    async def get_category_by_name(self, name: str) -> Optional[CategoryEntity]:
        """Get a category by name"""
        pass
    
    @abstractmethod
    async def mark_as_created(self, category_id: int) -> None:
        """Mark a category as created"""
        pass
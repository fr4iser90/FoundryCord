from abc import ABC, abstractmethod
from typing import Optional, List, Any

class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: int) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_discord_id(self, category_discord_id: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_guild_and_type(self, guild_id: str, category_type: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_type(self, category_type: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_guild(self, guild_id: str) -> List[Any]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Any]:
        pass
    
    @abstractmethod
    async def create(self, guild_id: str, category_id: str, category_name: str, category_type: str = "homelab") -> Any:
        pass
    
    @abstractmethod
    async def update(self, category) -> Any:
        pass
    
    @abstractmethod
    async def delete(self, category) -> None:
        pass
    
    @abstractmethod
    async def save_or_update(self, guild_id: str, category_id: str, category_name: str, category_type: str) -> Any:
        pass
    
    @abstractmethod
    async def get_all_categories(self) -> List[Any]:
        """Get all categories"""
        pass
    
    @abstractmethod
    async def get_enabled_categories(self) -> List[Any]:
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
    async def get_category_by_name(self, name: str) -> Optional[Any]:
        """Get a category by name"""
        pass
    
    @abstractmethod
    async def mark_as_created(self, category_id: int) -> None:
        """Mark a category as created"""
        pass
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
from abc import ABC, abstractmethod
from typing import Optional, List, Any

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_discord_id(self, discord_id: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Any]:
        pass
    
    @abstractmethod
    async def get_by_discord_name(self, discord_name: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def create(self, discord_id: str, username: str, role: str = "user") -> Any:
        pass
    
    @abstractmethod
    async def update(self, user) -> Any:
        pass
    
    @abstractmethod
    async def delete(self, user) -> None:
        pass
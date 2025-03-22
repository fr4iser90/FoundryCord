from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class GuildConfigRepository(ABC):
    @abstractmethod
    async def get_by_guild_id(self, guild_id: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Any]:
        pass
    
    @abstractmethod
    async def create_or_update(self, guild_id: str, guild_name: str, 
                              features: Dict[str, bool] = None, 
                              settings: Dict[str, Any] = None) -> Any:
        pass
    
    @abstractmethod
    async def delete(self, config) -> None:
        pass
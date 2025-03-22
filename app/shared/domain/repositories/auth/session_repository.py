from abc import ABC, abstractmethod
from typing import Optional, List, Any
from datetime import datetime

class SessionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, session_id: int) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Any]:
        pass
    
    @abstractmethod
    async def get_active_sessions(self) -> List[Any]:
        pass
    
    @abstractmethod
    async def create(self, user_id: str, token: str, expires_at: datetime) -> Any:
        pass
    
    @abstractmethod
    async def update(self, session_obj) -> Any:
        pass
    
    @abstractmethod
    async def delete(self, session_obj) -> None:
        pass
    
    @abstractmethod
    async def delete_expired(self) -> int:
        pass
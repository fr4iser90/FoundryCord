from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

class AuditLogRepository(ABC):
    @abstractmethod
    async def get_by_id(self, log_id: int) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Any]:
        pass
    
    @abstractmethod
    async def get_by_action(self, action: str, limit: int = 100) -> List[Any]:
        pass
    
    @abstractmethod
    async def get_recent_logs(self, limit: int = 100) -> List[Any]:
        pass
    
    @abstractmethod
    async def create(self, user_id: str, action: str, details: Dict[str, Any]) -> Any:
        pass
    
    @abstractmethod
    async def delete_older_than(self, days: int) -> int:
        pass
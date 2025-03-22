from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class DashboardRepository(ABC):
    @abstractmethod
    async def get_dashboard_by_id(self, dashboard_id: int) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_dashboard_by_type(self, dashboard_type: str, guild_id: str = None) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_dashboards_by_channel(self, channel_id: int) -> List[Any]:
        pass
    
    @abstractmethod
    async def create_dashboard(self, title: str, dashboard_type: str, guild_id: str, 
                              channel_id: int, **kwargs) -> Any:
        pass
    
    @abstractmethod
    async def update_dashboard(self, dashboard) -> Any:
        pass
    
    @abstractmethod
    async def delete_dashboard(self, dashboard) -> None:
        pass
    
    # Add other methods as needed
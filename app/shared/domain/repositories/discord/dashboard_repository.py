from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity

class DashboardRepository(ABC):
    @abstractmethod
    async def get_dashboard_by_id(self, dashboard_id: int) -> Optional[DashboardEntity]:
        pass
    
    @abstractmethod
    async def get_dashboard_by_type(self, dashboard_type: str, guild_id: str = None) -> Optional[DashboardEntity]:
        pass
    
    @abstractmethod
    async def get_dashboards_by_channel(self, channel_id: int) -> List[DashboardEntity]:
        pass
    
    @abstractmethod
    async def create_dashboard(self, name: str, dashboard_type: str, guild_id: str, 
                              channel_id: int, **kwargs) -> DashboardEntity:
        pass
    
    @abstractmethod
    async def update_dashboard(self, dashboard: DashboardEntity) -> DashboardEntity:
        pass
    
    @abstractmethod
    async def delete_dashboard(self, dashboard: DashboardEntity) -> None:
        pass
    
    @abstractmethod
    async def get_all_dashboards(self) -> List[DashboardEntity]:
        pass
    
    @abstractmethod
    async def get_dashboards_by_guild(self, guild_id: str) -> List[DashboardEntity]:
        pass
    
    @abstractmethod
    async def get_active_dashboards(self) -> List[DashboardEntity]:
        pass
    
    # Add other methods as needed
from abc import ABC, abstractmethod
from typing import List, Optional
from app.web.domain.dashboard_builder.models import Dashboard, DashboardCreate, DashboardUpdate, Widget, WidgetCreate


class DashboardRepository(ABC):
    """Interface for dashboard repository"""
    
    @abstractmethod
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID"""
        pass
        
    @abstractmethod
    async def get_user_dashboards(self, user_id: str) -> List[Dashboard]:
        """Get all dashboards for a user"""
        pass
        
    @abstractmethod
    async def create_dashboard(self, user_id: str, dashboard: DashboardCreate) -> Dashboard:
        """Create a new dashboard"""
        pass
        
    @abstractmethod
    async def update_dashboard(self, dashboard_id: str, dashboard: DashboardUpdate) -> Optional[Dashboard]:
        """Update an existing dashboard"""
        pass
        
    @abstractmethod
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard"""
        pass

    @abstractmethod
    async def add_widget(self, dashboard_id: str, widget: WidgetCreate) -> Optional[Widget]:
        """Add a widget to a dashboard"""
        pass
        
    @abstractmethod
    async def update_widget(self, widget_id: str, widget_data: dict) -> Optional[Widget]:
        """Update a widget"""
        pass
        
    @abstractmethod
    async def delete_widget(self, widget_id: str) -> bool:
        """Delete a widget"""
        pass 
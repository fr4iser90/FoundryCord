"""Repository interface for dashboards."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
import json
import asyncio
from sqlalchemy import text

from app.bot.domain.dashboards.models.orm_models import Dashboard
from app.shared.interface.logging.api import get_db_logger
from app.shared.infrastructure.database.management.connection import DatabaseConnection

logger = get_db_logger()

class IDashboardRepository(ABC):
    """Repository interface for dashboards."""
    
    @abstractmethod
    async def get_dashboard_by_id(self, dashboard_id: int) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        pass
        
    @abstractmethod
    async def get_dashboard_by_channel(self, channel_id: int) -> Optional[Dashboard]:
        """Get a dashboard by channel ID."""
        pass
        
    @abstractmethod
    async def get_all_dashboards(self) -> List[Dashboard]:
        """Get all dashboards."""
        pass
        
    @abstractmethod
    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Optional[Dashboard]:
        """Create a new dashboard."""
        pass
        
    @abstractmethod
    async def update_dashboard(self, dashboard_id: int, dashboard_data: Dict[str, Any]) -> Optional[Dashboard]:
        """Update a dashboard."""
        pass
        
    @abstractmethod
    async def delete_dashboard(self, dashboard_id: int) -> bool:
        """Delete a dashboard."""
        pass


class DashboardRepository(IDashboardRepository):
    """Repository implementation for dashboards using SQLAlchemy."""
    
    def __init__(self, session_factory=None):
        """Initialize the dashboard repository."""
        # We don't need to store the session_factory since we're using DatabaseConnection
        self.db = DatabaseConnection()
        logger.info("Dashboard repository initialized with session factory")
    
    async def get_dashboard_by_id(self, dashboard_id: int) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        try:
            query = f"SELECT * FROM dashboards WHERE id = {dashboard_id}"
            results = await self.db.fetch(query)
            
            if not results:
                return None
                
            return self._create_dashboard_from_row(results[0])
                
        except Exception as e:
            logger.error(f"Error getting dashboard by ID {dashboard_id}: {e}")
            return None
    
    async def get_dashboard_by_channel(self, channel_id: int) -> Optional[Dashboard]:
        """Get a dashboard by channel ID."""
        try:
            query = f"SELECT * FROM dashboards WHERE channel_id = {channel_id}"
            results = await self.db.fetch(query)
            
            if not results:
                return None
                
            return self._create_dashboard_from_row(results[0])
                
        except Exception as e:
            logger.error(f"Error getting dashboard by channel ID {channel_id}: {e}")
            return None
    
    async def get_all_dashboards(self) -> List[Dashboard]:
        """Get all dashboards."""
        dashboards = []
        
        try:
            query = "SELECT * FROM dashboards"
            results = await self.db.fetch(query)
            
            for row in results:
                dashboard = self._create_dashboard_from_row(row)
                dashboards.append(dashboard)
            
            return dashboards
                
        except Exception as e:
            logger.error(f"Error getting all dashboards: {e}")
            return []
    
    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Optional[Dashboard]:
        """Create a new dashboard."""
        # Implementation using self.db.execute
        pass
        
    async def update_dashboard(self, dashboard_id: int, dashboard_data: Dict[str, Any]) -> Optional[Dashboard]:
        """Update a dashboard."""
        # Implementation using self.db.execute
        pass
        
    async def delete_dashboard(self, dashboard_id: int) -> bool:
        """Delete a dashboard."""
        # Implementation using self.db.execute
        pass
    
    def _create_dashboard_from_row(self, row_dict: Dict[str, Any]) -> Dashboard:
        """Create a Dashboard object from a database row."""
        # Create a Dashboard object from the row data
        return Dashboard(
            id=row_dict.get('id'),
            dashboard_type=row_dict.get('dashboard_type'),
            name=row_dict.get('name'),
            description=row_dict.get('description'),
            guild_id=row_dict.get('guild_id'),
            channel_id=row_dict.get('channel_id'),
            is_active=row_dict.get('is_active', True),
            update_frequency=row_dict.get('update_frequency', 300),
            config=row_dict.get('config', {})
        )
        
    # Add other repository methods as needed... 
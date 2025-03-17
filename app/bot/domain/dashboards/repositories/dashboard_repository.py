"""Repository interface for dashboards."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
import json
import asyncio

from app.bot.domain.dashboards.models.dashboard_model import DashboardModel
from app.bot.domain.dashboards.models.component_model import ComponentModel
from app.bot.domain.dashboards.models.data_source_model import DataSourceModel

from app.shared.infrastructure.database.management.connection import get_session
from app.shared.infrastructure.database.models import Dashboard as DashboardEntity
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.api import get_db

logger = get_bot_logger()

class DashboardRepository(ABC):
    """Repository interface for dashboard storage."""
    
    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> Optional[DashboardModel]:
        """Get a dashboard by ID."""
        pass
    
    @abstractmethod
    async def get_by_type(self, dashboard_type: str, guild_id: str) -> Optional[DashboardModel]:
        """Get a dashboard by type and guild ID."""
        pass
    
    @abstractmethod
    async def get_by_channel_id(self, channel_id: int) -> Optional[DashboardModel]:
        """Get a dashboard by channel ID."""
        pass
    
    @abstractmethod
    async def list_all(self, guild_id: Optional[str] = None) -> List[DashboardModel]:
        """List all dashboards, optionally filtered by guild ID."""
        pass
    
    @abstractmethod
    async def save(self, dashboard: DashboardModel) -> DashboardModel:
        """Save a dashboard."""
        pass
    
    @abstractmethod
    async def delete(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        pass

class DashboardRepository:
    """Repository for storing and retrieving dashboard configurations."""
    
    def __init__(self):
        self.db = get_db()
        self.logger = get_bot_logger()
        
    async def get_by_id(self, dashboard_id: Union[str, int]) -> Optional[DashboardModel]:
        """Get a dashboard by ID."""
        try:
            async with self.db.transaction() as tx:
                # Use the transaction directly for queries
                query = "SELECT * FROM dashboards WHERE id = $1"
                result = await tx.fetch(query, int(dashboard_id))
                
                if not result or len(result) == 0:
                    return None
                    
                # Convert to domain model
                # This is simplified - in reality, you'd need to also fetch components
                dashboard_data = dict(result[0])
                
                # Get components
                components_query = """
                    SELECT c.*, l.* 
                    FROM dashboard_components c
                    LEFT JOIN component_layouts l ON c.id = l.component_id
                    WHERE c.dashboard_id = $1
                """
                components = await tx.fetch(components_query, dashboard_id)
                
                # Build a complete dashboard model
                dashboard = self._build_dashboard_model(dashboard_data, components)
                return dashboard
                
        except Exception as e:
            self.logger.error(f"Error getting dashboard by ID {dashboard_id}: {e}")
            return None
            
    async def get_by_channel_id(self, channel_id: Union[str, int]) -> Optional[DashboardModel]:
        """Get a dashboard by channel ID."""
        try:
            async with self.db.transaction() as tx:
                query = "SELECT * FROM dashboards WHERE channel_id = $1"
                result = await tx.fetch(query, str(channel_id))
                
                if not result or len(result) == 0:
                    return None
                    
                # Convert to domain model  
                dashboard_data = dict(result[0])
                dashboard_id = dashboard_data['id']
                
                # Get components
                components_query = """
                    SELECT c.*, l.* 
                    FROM dashboard_components c
                    LEFT JOIN component_layouts l ON c.id = l.component_id
                    WHERE c.dashboard_id = $1
                """
                components = await tx.fetch(components_query, dashboard_id)
                
                # Build complete dashboard model
                dashboard = self._build_dashboard_model(dashboard_data, components)
                return dashboard
                
        except Exception as e:
            self.logger.error(f"Error getting dashboard by channel ID {channel_id}: {e}")
            return None
    
    async def get_all_dashboards(self) -> List[DashboardModel]:
        """Get all dashboards."""
        try:
            dashboards = []
            
            async with self.db.transaction() as tx:
                # Get all dashboards
                query = "SELECT * FROM dashboards"
                results = await tx.fetch(query)
                
                if not results:
                    return []
                    
                # For each dashboard, get its components
                for row in results:
                    dashboard_data = dict(row)
                    dashboard_id = dashboard_data['id']
                    
                    # Get components
                    components_query = """
                        SELECT c.*, l.* 
                        FROM dashboard_components c
                        LEFT JOIN component_layouts l ON c.id = l.component_id
                        WHERE c.dashboard_id = $1
                    """
                    components = await tx.fetch(components_query, dashboard_id)
                    
                    # Build dashboard model
                    dashboard = self._build_dashboard_model(dashboard_data, components)
                    dashboards.append(dashboard)
                    
                return dashboards
                
        except Exception as e:
            self.logger.error(f"Error getting all dashboards: {e}")
            return []
    
    async def save(self, dashboard: DashboardModel) -> Optional[DashboardModel]:
        """Save a dashboard."""
        try:
            async with self.db.transaction() as tx:
                # Check if dashboard exists
                if dashboard.id and not isinstance(dashboard.id, str):
                    # Update existing dashboard
                    update_query = """
                        UPDATE dashboards
                        SET dashboard_type = $1, name = $2, description = $3,
                            guild_id = $4, channel_id = $5, is_active = $6,
                            update_frequency = $7, config = $8, updated_at = NOW()
                        WHERE id = $9
                        RETURNING *
                    """
                    
                    result = await tx.fetch(
                        update_query,
                        dashboard.type,
                        dashboard.title,
                        dashboard.description,
                        str(dashboard.guild_id) if dashboard.guild_id else None,
                        str(dashboard.channel_id) if dashboard.channel_id else None,
                        dashboard.is_active,
                        dashboard.update_frequency,
                        dashboard.config,
                        dashboard.id
                    )
                else:
                    # Create new dashboard
                    insert_query = """
                        INSERT INTO dashboards (
                            dashboard_type, name, description, guild_id, 
                            channel_id, is_active, update_frequency, config
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        RETURNING *
                    """
                    
                    result = await tx.fetch(
                        insert_query,
                        dashboard.type,
                        dashboard.title,
                        dashboard.description,
                        str(dashboard.guild_id) if dashboard.guild_id else None,
                        str(dashboard.channel_id) if dashboard.channel_id else None,
                        dashboard.is_active,
                        dashboard.update_frequency,
                        dashboard.config
                    )
                
                if not result or len(result) == 0:
                    return None
                    
                # Get the saved dashboard ID
                saved_dashboard = dict(result[0])
                dashboard_id = saved_dashboard['id']
                
                # Save components if they exist
                if hasattr(dashboard, 'components') and dashboard.components:
                    for component in dashboard.components:
                        await self._save_component(tx, component, dashboard_id)
                
                # Return the updated dashboard
                return await self.get_by_id(dashboard_id)
                
        except Exception as e:
            self.logger.error(f"Error saving dashboard: {e}")
            return None
    
    async def delete(self, dashboard_id: Union[str, int]) -> bool:
        """Delete a dashboard."""
        try:
            async with self.db.transaction() as tx:
                # Delete dashboard
                query = "DELETE FROM dashboards WHERE id = $1"
                await tx.execute(query, int(dashboard_id))
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting dashboard {dashboard_id}: {e}")
            return False
    
    async def _save_component(self, tx, component, dashboard_id: int):
        """Save a dashboard component."""
        try:
            if component.id and not isinstance(component.id, str):
                # Update existing component
                update_query = """
                    UPDATE dashboard_components
                    SET component_type = $1, title = $2, config = $3, updated_at = NOW()
                    WHERE id = $4
                    RETURNING id
                """
                
                result = await tx.fetch(
                    update_query,
                    component.type,
                    component.title,
                    component.config,
                    component.id
                )
                
                component_id = result[0]['id'] if result and len(result) > 0 else None
            else:
                # Create new component
                insert_query = """
                    INSERT INTO dashboard_components (
                        dashboard_id, component_type, title, config
                    ) VALUES ($1, $2, $3, $4)
                    RETURNING id
                """
                
                result = await tx.fetch(
                    insert_query,
                    dashboard_id,
                    component.type,
                    component.title,
                    component.config
                )
                
                component_id = result[0]['id'] if result and len(result) > 0 else None
            
            # Update layout if component was created/updated successfully
            if component_id:
                # Check if layout exists
                layout_check = """
                    SELECT id FROM component_layouts WHERE component_id = $1
                """
                layout_result = await tx.fetch(layout_check, component_id)
                
                if layout_result and len(layout_result) > 0:
                    # Update existing layout
                    layout_query = """
                        UPDATE component_layouts
                        SET row_position = $1, col_position = $2,
                            width = $3, height = $4
                        WHERE component_id = $5
                    """
                    
                    await tx.execute(
                        layout_query,
                        component.position_y,
                        component.position_x,
                        component.width,
                        component.height,
                        component_id
                    )
                else:
                    # Create new layout
                    layout_query = """
                        INSERT INTO component_layouts (
                            component_id, row_position, col_position, width, height
                        ) VALUES ($1, $2, $3, $4, $5)
                    """
                    
                    await tx.execute(
                        layout_query,
                        component_id,
                        component.position_y,
                        component.position_x,
                        component.width,
                        component.height
                    )
                    
            return component_id
            
        except Exception as e:
            self.logger.error(f"Error saving component: {e}")
            return None
    
    def _build_dashboard_model(self, dashboard_data, components=None):
        """Build a dashboard domain model from database data."""
        # Create base dashboard
        dashboard = DashboardModel(
            id=dashboard_data.get('id'),
            title=dashboard_data.get('name'),
            type=dashboard_data.get('dashboard_type'),
            description=dashboard_data.get('description'),
            guild_id=dashboard_data.get('guild_id'),
            channel_id=dashboard_data.get('channel_id'),
            is_active=dashboard_data.get('is_active', True),
            update_frequency=dashboard_data.get('update_frequency', 300),
            config=dashboard_data.get('config', {})
        )
        
        # Add components if they exist
        if components:
            for comp_data in components:
                from app.bot.domain.dashboards.models.component_model import ComponentModel
                
                component = ComponentModel(
                    id=comp_data.get('id'),
                    type=comp_data.get('component_type'),
                    title=comp_data.get('title'),
                    position_x=comp_data.get('col_position', 0),
                    position_y=comp_data.get('row_position', 0),
                    width=comp_data.get('width', 1),
                    height=comp_data.get('height', 1),
                    config=comp_data.get('config', {})
                )
                
                dashboard.add_component(component)
                
        return dashboard 
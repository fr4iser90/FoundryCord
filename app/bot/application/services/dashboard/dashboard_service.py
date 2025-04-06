"""Dashboard service for coordinating dashboard operations."""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.shared.infrastructure.models.dashboard.entities.dashboard_entity import DashboardEntity
from app.shared.domain.repositories import DashboardRepository
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry
from app.shared.infrastructure.database.core.config import get_session

class DashboardService:
    """Core service for dashboard operations."""
    
    def __init__(self, 
                 bot,
                 repository: DashboardRepository,
                 component_registry: ComponentRegistry,
                 data_source_registry: DataSourceRegistry):
        self.bot = bot
        self.repository = repository
        self.component_registry = component_registry
        self.data_source_registry = data_source_registry
        
    async def get_dashboard(self, dashboard_id: str) -> Optional[DashboardEntity]:
        """Get a dashboard by ID."""
        return await self.repository.get_by_id(dashboard_id)
    
    async def get_dashboard_by_channel(self, channel_id: int) -> Optional[DashboardEntity]:
        """Get a dashboard for a channel."""
        return await self.repository.get_by_channel_id(channel_id)
    
    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> DashboardEntity:
        """Create a new dashboard from configuration."""
        # Convert raw data to domain model
        dashboard = self._create_dashboard_entity(dashboard_data)
        
        # Save to repository
        saved_dashboard = await self.repository.save(dashboard)
        
        logger.info(f"Created new dashboard: {saved_dashboard.id} ({saved_dashboard.title})")
        return saved_dashboard
    
    async def update_dashboard(self, dashboard_id: str, dashboard_data: Dict[str, Any]) -> Optional[DashboardEntity]:
        """Update an existing dashboard."""
        dashboard = await self.repository.get_by_id(dashboard_id)
        if not dashboard:
            logger.warning(f"Attempted to update non-existent dashboard: {dashboard_id}")
            return None
            
        # Update dashboard properties
        for key, value in dashboard_data.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
                
        # Update timestamp
        dashboard.updated_at = datetime.now()
        
        # Save updated dashboard
        updated_dashboard = await self.repository.save(dashboard)
        
        logger.info(f"Updated dashboard: {updated_dashboard.id}")
        return updated_dashboard
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        result = await self.repository.delete(dashboard_id)
        if result:
            logger.info(f"Deleted dashboard: {dashboard_id}")
        return result
    
    async def get_all_dashboards(self) -> List[DashboardEntity]:
        """Get all dashboards."""
        try:
            return await self.repository.get_all_dashboards()
        except Exception as e:
            logger.error(f"Error getting all dashboards: {e}")
            return []
    
    async def refresh_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Refresh data for a dashboard."""
        dashboard = await self.repository.get_by_id(dashboard_id)
        if not dashboard:
            logger.warning(f"Attempted to refresh non-existent dashboard: {dashboard_id}")
            return {}
            
        # Collect data from all data sources
        data = {}
        for source_id, source_config in dashboard.data_sources.items():
            try:
                data_source = self.data_source_registry.get_data_source(source_config.type)
                if data_source:
                    result = await data_source.fetch_data(source_config.params)
                    data[source_id] = result.data
                else:
                    logger.warning(f"Data source type not found: {source_config.type}")
            except Exception as e:
                logger.error(f"Error fetching data from source {source_id}: {e}")
                
        return data
    
    def _create_dashboard_entity(self, data: Dict[str, Any]) -> DashboardEntity:
        """Convert dictionary data to a DashboardEntity."""
        from app.shared.infrastructure.models.dashboard.entities import (
            DashboardEntity, ComponentConfig, DataSourceConfig, LayoutItem, ComponentType
        )
        
        # Create base dashboard
        dashboard = DashboardEntity(
            id=data.get('id'),
            type=data.get('type'),
            title=data.get('title'),
            description=data.get('description'),
            channel_id=data.get('channel_id'),
            guild_id=data.get('guild_id'),
            channel_name=data.get('channel_name'),
            category_name=data.get('category_name'),
            message_id=data.get('message_id'),
            embed=data.get('embed', {})
        )
        
        # Add components
        for comp_data in data.get('components', []):
            component = ComponentConfig(
                id=comp_data.get('id'),
                type=ComponentType(comp_data.get('type')),
                title=comp_data.get('title'),
                data_source_id=comp_data.get('data_source_id'),
                config=comp_data.get('config', {})
            )
            dashboard.add_component(component)
            
        # Add data sources
        for source_id, source_data in data.get('data_sources', {}).items():
            data_source = DataSourceConfig(
                id=source_id,
                type=source_data.get('type'),
                refresh_interval=source_data.get('refresh_interval', 60),
                params=source_data.get('params', {})
            )
            dashboard.add_data_source(data_source)
            
        # Add layout
        for layout_data in data.get('layout', []):
            layout_item = LayoutItem(
                component_id=layout_data.get('component_id'),
                row=layout_data.get('row', 0),
                col=layout_data.get('col', 0),
                width=layout_data.get('width', 1),
                height=layout_data.get('height', 1)
            )
            dashboard.add_layout_item(layout_item)
            
        # Add interactive components
        dashboard.interactive_components = data.get('interactive_components', [])
        
        return dashboard 

    async def ensure_dashboard_tables_exist(self):
        """Ensure all required dashboard tables exist in the database."""
        try:
            # Create dashboards table first
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS dashboards (
                    id SERIAL PRIMARY KEY,
                    dashboard_type VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    guild_id VARCHAR(50),
                    channel_id VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    update_frequency INTEGER DEFAULT 300,
                    config JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes separately
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboards_dashboard_type 
                ON dashboards(dashboard_type)
            """)
            
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboards_guild_id 
                ON dashboards(guild_id)
            """)
            
            # Create dashboard_components table before component_layouts
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_components (
                    id SERIAL PRIMARY KEY,
                    dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE CASCADE,
                    component_type VARCHAR(50) NOT NULL,
                    title VARCHAR(100),
                    config JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Now create component_layouts
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS component_layouts (
                    id SERIAL PRIMARY KEY,
                    component_id INTEGER REFERENCES dashboard_components(id) ON DELETE CASCADE,
                    row_position INTEGER DEFAULT 0,
                    col_position INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 1,
                    height INTEGER DEFAULT 1,
                    style VARCHAR(50),
                    additional_props JSONB
                )
            """)
            
            self.logger.info("Dashboard tables created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error ensuring dashboard tables exist: {e}")
            return False 
"""Repository for storing and retrieving dashboard configurations."""
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

#from app.shared.infrastructure.database.models.config import get_config, set_config
from app.shared.infrastructure.database.core.connection import get_config, set_config

# Import models
from app.shared.infrastructure.database.models import Dashboard, DashboardComponent
from app.shared.infrastructure.database.core.config import get_session

class DashboardRepository:
    """Repository for storing and retrieving dashboard configurations."""
    
    def __init__(self, bot):
        self.bot = bot
        self.session_factory = get_session
        self.initialized = False
        
    async def initialize(self):
        """Initialize the dashboard repository."""
        self.initialized = True
        logger.info("Dashboard repository initialized")
        return True
        
    async def get_dashboard_by_id(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        async with self.session_factory() as session:
            stmt = select(Dashboard).where(Dashboard.id == dashboard_id)
            result = await session.execute(stmt)
            return result.scalars().first()
            
    async def get_dashboard_by_channel_and_type(self, channel_id: int, dashboard_type: str) -> Optional[Dashboard]:
        """Get a dashboard by channel ID and type."""
        async with self.session_factory() as session:
            stmt = select(Dashboard).where(
                Dashboard.channel_id == channel_id,
                Dashboard.dashboard_type == dashboard_type
            )
            result = await session.execute(stmt)
            return result.scalars().first()
            
    async def get_components_for_dashboard(self, dashboard_id: str) -> List[DashboardComponent]:
        """Get all components for a dashboard."""
        async with self.session_factory() as session:
            stmt = select(DashboardComponent).where(DashboardComponent.dashboard_id == dashboard_id)
            result = await session.execute(stmt)
            return result.scalars().all()
            
    async def update_dashboard(self, dashboard_id: str, data: Dict[str, Any]) -> bool:
        """Update a dashboard."""
        async with self.session_factory() as session:
            try:
                stmt = update(Dashboard).where(Dashboard.id == dashboard_id).values(**data)
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating dashboard {dashboard_id}: {e}")
                await session.rollback()
                return False
        
    async def get_dashboard_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get a dashboard configuration by ID."""
        try:
            config_key = f"dashboard_config_{config_id}"
            config_json = await get_config(config_key)
            
            if not config_json:
                logger.warning(f"Dashboard config not found: {config_id}")
                return None
                
            return json.loads(config_json)
            
        except Exception as e:
            logger.error(f"Error getting dashboard config {config_id}: {e}")
            return None
            
    async def save_dashboard_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Save a dashboard configuration."""
        try:
            config_id = config.get('id')
            
            if not config_id:
                config_id = f"dashboard_{uuid.uuid4().hex}"
                config['id'] = config_id
                
            # Add metadata
            config['updated_at'] = datetime.now().isoformat()
            
            # Save to database
            config_key = f"dashboard_config_{config_id}"
            await set_config(config_key, json.dumps(config))
            
            logger.info(f"Saved dashboard config: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Error saving dashboard config: {e}")
            return None
            
    async def list_dashboard_configs(self) -> List[Dict[str, Any]]:
        """List all dashboard configurations."""
        try:
            # This is a simplistic implementation
            # In a real application, we'd need a better way to query all dashboards
            # For now, we'll just return an empty list since we haven't implemented
            # a proper way to list all config keys with a prefix
            return []
            
        except Exception as e:
            logger.error(f"Error listing dashboard configs: {e}")
            return []
            
    async def delete_dashboard_config(self, config_id: str) -> bool:
        """Delete a dashboard configuration."""
        try:
            config_key = f"dashboard_config_{config_id}"
            await set_config(config_key, None)
            
            logger.info(f"Deleted dashboard config: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dashboard config {config_id}: {e}")
            return False 
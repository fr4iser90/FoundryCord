"""Repository for storing and retrieving dashboard configurations."""
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()


from app.shared.infrastructure.database.core.connection import get_config, set_config

# Import models
from app.shared.infrastructure.models import DashboardEntity, DashboardComponentEntity
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
        logger.info("DashboardEntity repository initialized")
        return True
        
    async def get_dashboard_by_id(self, dashboard_id: str) -> Optional[DashboardEntity]:
        """Get a dashboard by ID."""
        async with self.session_factory() as session:
            stmt = select(DashboardEntity).where(DashboardEntity.id == dashboard_id)
            result = await session.execute(stmt)
            return result.scalars().first()
            
    async def get_dashboard_by_channel_and_type(self, channel_id: int, dashboard_type: str) -> Optional[DashboardEntity]:
        """Get a dashboard by channel ID and type."""
        async with self.session_factory() as session:
            stmt = select(DashboardEntity).where(
                DashboardEntity.channel_id == channel_id,
                DashboardEntity.dashboard_type == dashboard_type
            )
            result = await session.execute(stmt)
            return result.scalars().first()
            
    async def get_components_for_dashboard(self, dashboard_id: str) -> List[DashboardComponentEntity]:
        """Get all components for a dashboard."""
        async with self.session_factory() as session:
            stmt = select(DashboardComponentEntity).where(DashboardComponentEntity.dashboard_id == dashboard_id)
            result = await session.execute(stmt)
            return result.scalars().all()
            
    async def get_by_channel_id(self, channel_id: int) -> Optional[DashboardEntity]:
        """Get a dashboard entity by channel ID."""
        # Assuming channel_id in the DB is stored as string
        channel_id_str = str(channel_id) 
        async with self.session_factory() as session:
            try:
                stmt = select(DashboardEntity).where(DashboardEntity.channel_id == channel_id_str)
                result = await session.execute(stmt)
                entity = result.scalars().first()
                if entity:
                    logger.debug(f"Found DashboardEntity {entity.id} for channel_id {channel_id_str}")
                else:
                    logger.debug(f"No DashboardEntity found for channel_id {channel_id_str}")
                return entity
            except Exception as e:
                logger.error(f"Error fetching DashboardEntity for channel_id {channel_id_str}: {e}", exc_info=True)
                return None

    async def get_dashboard_by_channel_and_type(self, channel_id: int, dashboard_type: str) -> Optional[DashboardEntity]:
        """Get a dashboard by channel ID and type."""
        async with self.session_factory() as session:
            stmt = select(DashboardEntity).where(
                DashboardEntity.channel_id == channel_id,
                DashboardEntity.dashboard_type == dashboard_type
            )
            result = await session.execute(stmt)
            return result.scalars().first()
            
    async def create_dashboard_entity(self, **kwargs) -> Optional[DashboardEntity]:
        """Create a new DashboardEntity record."""
        # Ensure essential fields are present? Or rely on DB defaults/nulls?
        # Example: Ensure channel_id, guild_id, config_id are likely needed.
        required_fields = ['channel_id', 'guild_id', 'config_id', 'dashboard_type']
        if not all(field in kwargs for field in required_fields):
            logger.error(f"Missing required fields for create_dashboard_entity: Provided {list(kwargs.keys())}, Required {required_fields}")
            return None
            
        async with self.session_factory() as session:
            try:
                # Ensure IDs are strings if the model expects strings
                kwargs['channel_id'] = str(kwargs['channel_id'])
                kwargs['guild_id'] = str(kwargs['guild_id'])
                
                new_entity = DashboardEntity(**kwargs)
                session.add(new_entity)
                await session.flush() # Flush to get the ID potentially
                await session.refresh(new_entity)
                logger.info(f"Created DashboardEntity record ID: {new_entity.id} for channel {kwargs['channel_id']}, config {kwargs['config_id']}")
                await session.commit() # Commit the new entity
                return new_entity
            except Exception as e:
                logger.error(f"Error creating DashboardEntity: {e}", exc_info=True)
                await session.rollback()
                return None

    async def update_dashboard(self, dashboard_id: str, data: Dict[str, Any]) -> bool:
        """Update a dashboard."""
        async with self.session_factory() as session:
            try:
                stmt = update(DashboardEntity).where(DashboardEntity.id == dashboard_id).values(**data)
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
                logger.warning(f"DashboardEntity config not found: {config_id}")
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
                
            # Add metadata_json
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
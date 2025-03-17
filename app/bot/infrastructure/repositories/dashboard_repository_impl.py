"""Dashboard repository implementation for storing dashboard configurations."""
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class DashboardRepositoryImpl:
    """Repository for storing and retrieving dashboard configurations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_dashboard_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get dashboard configuration by ID."""
        from app.shared.infrastructure.database.models import Dashboard
        
        try:
            result = await self.session.execute(
                select(Dashboard).where(Dashboard.id == config_id)
            )
            dashboard = result.scalars().first()
            
            if not dashboard:
                return None
                
            # Parse JSON config
            config = json.loads(dashboard.config) if dashboard.config else {}
            
            # Add database fields
            config.update({
                'id': dashboard.id,
                'title': dashboard.title,
                'description': dashboard.description,
                'channel_id': dashboard.channel_id,
                'guild_id': dashboard.guild_id,
                'message_id': dashboard.message_id,
                'dashboard_type': dashboard.dashboard_type,
                'created_at': dashboard.created_at.isoformat(),
                'updated_at': dashboard.updated_at.isoformat()
            })
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting dashboard config {config_id}: {e}")
            return None
    
    async def save_dashboard_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Save dashboard configuration."""
        from app.shared.infrastructure.database.models import Dashboard
        
        try:
            config_id = config.get('id')
            
            # Create new ID if not provided
            if not config_id:
                config_id = str(uuid.uuid4())
                config['id'] = config_id
                
            # Check if config exists
            result = await self.session.execute(
                select(Dashboard).where(Dashboard.id == config_id)
            )
            existing = result.scalars().first()
            
            # Extract database fields
            db_fields = {
                'id': config_id,
                'title': config.get('title', 'Dashboard'),
                'description': config.get('description', ''),
                'dashboard_type': config.get('dashboard_type', 'dynamic'),
                'channel_id': config.get('channel_id'),
                'guild_id': config.get('guild_id'),
                'message_id': config.get('message_id')
            }
            
            # Remove database fields from config
            config_copy = config.copy()
            for field in db_fields:
                if field in config_copy:
                    del config_copy[field]
                    
            # Remove special fields
            for field in ['created_at', 'updated_at']:
                if field in config_copy:
                    del config_copy[field]
            
            if existing:
                # Update existing
                for key, value in db_fields.items():
                    setattr(existing, key, value)
                    
                existing.config = json.dumps(config_copy)
                existing.updated_at = datetime.now()
                
            else:
                # Create new
                new_dashboard = Dashboard(
                    **db_fields,
                    config=json.dumps(config_copy),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.session.add(new_dashboard)
                
            await self.session.commit()
            return config_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving dashboard config: {e}")
            return None
    
    async def delete_dashboard_config(self, config_id: str) -> bool:
        """Delete dashboard configuration."""
        from app.shared.infrastructure.database.models import Dashboard
        
        try:
            result = await self.session.execute(
                select(Dashboard).where(Dashboard.id == config_id)
            )
            dashboard = result.scalars().first()
            
            if not dashboard:
                logger.warning(f"Dashboard config not found for deletion: {config_id}")
                return False
                
            await self.session.delete(dashboard)
            await self.session.commit()
            
            logger.info(f"Deleted dashboard config: {config_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting dashboard config: {e}")
            return False
    
    async def get_dashboard_by_channel(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get dashboard configuration by channel ID."""
        from app.shared.infrastructure.database.models import Dashboard
        
        try:
            result = await self.session.execute(
                select(Dashboard).where(Dashboard.channel_id == channel_id)
            )
            dashboard = result.scalars().first()
            
            if not dashboard:
                return None
                
            return await self.get_dashboard_config(dashboard.id)
            
        except Exception as e:
            logger.error(f"Error getting dashboard by channel {channel_id}: {e}")
            return None
    
    async def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """Get all dashboard configurations."""
        from app.shared.infrastructure.database.models import Dashboard
        
        try:
            result = await self.session.execute(select(Dashboard))
            dashboards = result.scalars().all()
            
            configs = []
            for dashboard in dashboards:
                config = await self.get_dashboard_config(dashboard.id)
                if config:
                    configs.append(config)
                    
            return configs
            
        except Exception as e:
            logger.error(f"Error getting all dashboards: {e}")
            return []
    
    async def get_dashboards_by_type(self, dashboard_type: str) -> List[Dict[str, Any]]:
        """Get all dashboard configurations of a specific type."""
        from app.shared.infrastructure.database.models import Dashboard
        
        try:
            result = await self.session.execute(
                select(Dashboard).where(Dashboard.dashboard_type == dashboard_type)
            )
            dashboards = result.scalars().all()
            
            configs = []
            for dashboard in dashboards:
                config = await self.get_dashboard_config(dashboard.id)
                if config:
                    configs.append(config)
                    
            return configs
            
        except Exception as e:
            logger.error(f"Error getting dashboards by type {dashboard_type}: {e}")
            return [] 
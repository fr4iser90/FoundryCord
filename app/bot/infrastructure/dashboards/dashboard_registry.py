# app/bot/infrastructure/dashboards/dashboard_registry.py
from typing import Dict, List, Any, Optional
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardRegistry:
    """Central registry for all available dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_dashboards = {}
        self.dashboard_configs = {}
    
    async def initialize(self):
        """Load all dashboard configurations from database"""
        try:
            # Fetch all dashboard types from database
            async with self.bot.db_session() as session:
                from app.shared.infrastructure.database.repositories.dashboard_repository_impl import DashboardRepository
                repository = DashboardRepository(session)
                dashboard_types = await repository.get_all_dashboard_types()
                
                # Load config for each dashboard type
                for dashboard_type in dashboard_types:
                    self.dashboard_configs[dashboard_type] = await repository.get_dashboard_config(dashboard_type)
                
            logger.info(f"Loaded {len(self.dashboard_configs)} dashboard configurations")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize dashboard registry: {e}")
            return False
    
    async def activate_dashboard(self, dashboard_type: str, channel_id: int) -> Optional[Dict]:
        """Activate a dashboard for a specific channel"""
        try:
            if dashboard_type not in self.dashboard_configs:
                logger.warning(f"Dashboard type '{dashboard_type}' not found in registry")
                return None
            
            # Create the dashboard using the dynamic controller
            dashboard = await self.bot.dashboard_factory.create_dynamic(
                dashboard_type=dashboard_type,
                channel_id=channel_id,
                config=self.dashboard_configs[dashboard_type]
            )
            
            if dashboard:
                self.active_dashboards[channel_id] = dashboard
                await dashboard.setup()
                return dashboard
            
            return None
        except Exception as e:
            logger.error(f"Failed to activate dashboard {dashboard_type}: {e}")
            return None
    
    async def deactivate_dashboard(self, dashboard_type=None, channel_id=None):
        """Deactivate dashboard by type or channel ID"""
        try:
            # If channel_id is provided, deactivate that specific dashboard
            if channel_id is not None and channel_id in self.active_dashboards:
                dashboard = self.active_dashboards[channel_id]
                await dashboard.cleanup()
                del self.active_dashboards[channel_id]
                logger.info(f"Deactivated dashboard in channel {channel_id}")
                return True
            
            # If dashboard_type is provided, deactivate all dashboards of that type
            elif dashboard_type is not None:
                deactivated = False
                # Find all channels with this dashboard type
                channels_to_remove = []
                for ch_id, dashboard in self.active_dashboards.items():
                    if hasattr(dashboard, 'DASHBOARD_TYPE') and dashboard.DASHBOARD_TYPE == dashboard_type:
                        await dashboard.cleanup()
                        channels_to_remove.append(ch_id)
                        deactivated = True
                
                # Remove from active dashboards
                for ch_id in channels_to_remove:
                    del self.active_dashboards[ch_id]
                
                if deactivated:
                    logger.info(f"Deactivated all dashboards of type {dashboard_type}")
                return deactivated
            
            return False
        except Exception as e:
            logger.error(f"Failed to deactivate dashboard: {e}")
            return False
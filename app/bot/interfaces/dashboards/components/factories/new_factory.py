# app/bot/interfaces/dashboards/factories/dashboard_factory.py
from typing import Dict, Any, Optional
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardFactory:
    """Factory for creating dashboard instances"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def create_dynamic(self, dashboard_type: str, channel_id: int, config: Dict[str, Any]) -> Optional[Dict]:
        """Create a dynamic dashboard based on configuration"""
        try:
            from app.bot.interfaces.dashboards.controller.dynamic_dashboard import DynamicDashboardController
            
            # Get channel object
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.warning(f"Channel {channel_id} not found")
                return None
            
            # Create dashboard controller
            dashboard = DynamicDashboardController(self.bot, dashboard_type)
            dashboard.config = config
            dashboard.channel = channel
            
            return {
                "dashboard": dashboard,
                "type": dashboard_type,
                "channel_id": channel_id
            }
        except Exception as e:
            logger.error(f"Failed to create dashboard {dashboard_type}: {e}")
            return None
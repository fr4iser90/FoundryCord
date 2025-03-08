from typing import Dict, Any
from infrastructure.logging import logger
from infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from infrastructure.factories.discord_ui import DashboardFactory
from .base_workflow import BaseWorkflow

class DashboardWorkflow(BaseWorkflow):
    def __init__(self, bot):
        self.bot = bot
        self.dashboard_factory = self.bot.component_factory.factories['dashboard']
        
    async def initialize(self):
        """Initialize all dashboard components"""
        try:
            logger.debug("Starting dashboard workflow initialization")
            dashboards = {}
            
            for channel_name, config in DASHBOARD_MAPPINGS.items():
                if config['auto_create']:
                    try:
                        dashboard = self.bot.factory.create_service(
                            f"Dashboard_{channel_name}",
                            config['setup']
                        )
                        if dashboard:
                            dashboards[channel_name] = dashboard
                            await self.bot.lifecycle._initialize_service(dashboard)
                    except Exception as e:
                        logger.error(f"Failed to initialize dashboard for {channel_name}: {e}")
            
            return dashboards
            
        except Exception as e:
            logger.error(f"Dashboard workflow initialization failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup dashboard resources"""
        try:
            logger.debug("Starting dashboard cleanup")
            # Cleanup logic for dashboards
            if hasattr(self.bot, 'dashboards'):
                for name, dashboard in self.bot.dashboards.items():
                    try:
                        if hasattr(dashboard, 'cleanup'):
                            await dashboard.cleanup()
                    except Exception as e:
                        logger.error(f"Error cleaning up dashboard {name}: {e}")
        except Exception as e:
            logger.error(f"Dashboard cleanup failed: {e}")
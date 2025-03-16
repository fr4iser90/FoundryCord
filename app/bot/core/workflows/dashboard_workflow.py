from typing import Dict, Any
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from app.bot.infrastructure.factories.service.service_resolver import ServiceResolver
from .base_workflow import BaseWorkflow
from app.bot.application.services.dashboard import dynamic_minecraft_setup

class DashboardWorkflow(BaseWorkflow):
    def __init__(self, bot):
        self.bot = bot
        self.dashboard_factory = self.bot.component_factory.factories['dashboard']
        
    async def initialize(self):
        """Initialize all dashboard components"""
        try:
            logger.debug("Starting dashboard workflow initialization")
            dashboards = {}
            
            # Dynamically resolve and initialize dashboards using the factory pattern
            for channel_name, config in DASHBOARD_MAPPINGS.items():
                if config['auto_create']:
                    try:
                        # Resolve setup function through service resolver (factory pattern)
                        setup_func = await ServiceResolver.resolve_dashboard_setup(
                            self.bot, 
                            config['dashboard_type']
                        )
                        
                        if not setup_func:
                            logger.error(f"No setup function found for dashboard {channel_name}")
                            continue
                            
                        # Create through factory
                        dashboard = self.bot.factory.create_service(
                            f"Dashboard_{channel_name}",
                            setup_func
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

    async def execute(self) -> None:
        """Initialize all dashboard services"""
        try:
            logger.info("Initializing dashboard services...")
            
            # Initialize existing dashboard services
            self.bot.welcome_dashboard_service = await welcome_setup(self.bot)
            self.bot.monitoring_dashboard_service = await monitoring_setup(self.bot)
            self.bot.project_dashboard_service = await project_setup(self.bot)
            self.bot.gamehub_dashboard_service = await gameservers_setup(self.bot)
            
            # Initialize your new service
            self.bot.dynamic_minecraft_dashboard_service = await dynamic_minecraft_setup(self.bot)
            
            logger.info("Dashboard services initialized")
        except Exception as e:
            logger.error(f"Error initializing dashboard services: {e}")
            raise
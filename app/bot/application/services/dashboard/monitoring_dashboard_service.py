from typing import Dict, Any
from nextcord.ext import commands
from infrastructure.logging import logger
from infrastructure.factories.discord_ui.dashboard_factory import DashboardFactory
from domain.monitoring.collectors import system_collector, service_collector
from interfaces.dashboards.ui.monitoring_dashboard import MonitoringDashboardUI

class MonitoringDashboardService:
    """Service für das Monitoring Dashboard"""
    
    def __init__(self, bot, dashboard_factory: DashboardFactory):
        self.bot = bot
        self.dashboard_factory = dashboard_factory
        self.initialized = False
        self.dashboard_ui = None
        
    async def initialize(self) -> None:
        """Initialisiert den Service"""
        try:
            # Direkt die Collector-Module verwenden statt Factory-Methoden
            self.system_collector = system_collector
            self.service_collector = service_collector
            
            # Initialize UI component
            self.dashboard_ui = MonitoringDashboardUI(self.bot).set_service(self)
            await self.dashboard_ui.initialize()
            
            self.initialized = True
            logger.info("Monitoring Dashboard Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Dashboard Service: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """Holt den System-Status über die Collectors"""
        if not self.initialized:
            await self.initialize()
            
        try:
            logger.debug("Collecting system data for monitoring dashboard")
            system_data = await system_collector.collect_system_data()
            
            logger.debug("Collecting service data for monitoring dashboard")
            service_data = await service_collector.collect_service_data()
            
            return {
                'system': system_data,
                'services': service_data,
            }
        except Exception as e:
            logger.error(f"Error collecting system status: {e}")
            raise
            
    async def display_dashboard(self) -> None:
        """Display the dashboard using the UI component"""
        if not self.dashboard_ui:
            logger.error("Dashboard UI not initialized")
            return
            
        await self.dashboard_ui.display_dashboard()

async def setup(bot):
    """Setup function for the Monitoring Dashboard service"""
    try:
        dashboard_factory = bot.dashboard_factory
        service = MonitoringDashboardService(bot, dashboard_factory)
        await service.initialize()
        
        # Display the dashboard after initialization
        await service.display_dashboard()
        
        logger.info("Monitoring Dashboard service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Monitoring Dashboard service: {e}")
        raise
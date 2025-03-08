from typing import Dict, Any
from nextcord.ext import commands
from infrastructure.logging import logger
from infrastructure.factories.discord_ui.dashboard_factory import DashboardFactory
from domain.monitoring.collectors import system_collector, service_collector

class MonitoringDashboardService:
    """Service für das Monitoring Dashboard"""
    
    def __init__(self, bot, dashboard_factory: DashboardFactory):
        self.bot = bot
        self.dashboard_factory = dashboard_factory
        self.initialized = False
        
    async def initialize(self) -> None:
        """Initialisiert den Service"""
        try:
            # Collectors über Factory erstellen
            self.system_collector = await self.dashboard_factory.create_system_collector()
            self.service_collector = await self.dashboard_factory.create_service_collector()
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
            system_data = await self.system_collector.collect()
            service_data = await self.service_collector.collect()
            
            return {
                'system': system_data,
                'services': service_data,
            }
        except Exception as e:
            logger.error(f"Error collecting system status: {e}")
            raise

async def setup(bot):
    """Setup function for the Monitoring Dashboard service"""
    try:
        dashboard_factory = bot.dashboard_factory
        service = MonitoringDashboardService(bot, dashboard_factory)
        await service.initialize()
        logger.info("Monitoring Dashboard service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Monitoring Dashboard service: {e}")
        raise
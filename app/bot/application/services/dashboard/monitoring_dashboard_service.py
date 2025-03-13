from typing import Dict, Any
from nextcord.ext import commands
from app.shared.logging import logger
from app.bot.infrastructure.factories.discord_ui.dashboard_factory import DashboardFactory
from app.bot.infrastructure.factories.monitoring import CollectorFactory

from app.bot.interfaces.dashboards.controller.monitoring_dashboard import MonitoringDashboardController

class MonitoringDashboardService:
    """Service für das Monitoring Dashboard"""
    
    def __init__(self, bot, dashboard_factory: DashboardFactory):
        self.bot = bot
        self.dashboard_factory = dashboard_factory
        self.collector_factory = CollectorFactory()
        self.initialized = False
        self.dashboard_ui = None
        
    async def initialize(self) -> None:
        """Initialisiert den Service"""
        try:
            # Get collectors through factory
            self.system_collector = self.collector_factory.create('system')
            self.service_collector = self.collector_factory.create('service')
            
            # Initialize UI component
            self.dashboard_ui = MonitoringDashboardController(self.bot).set_service( self)
            await self.dashboard_ui.initialize()
            
            self.initialized = True
            logger.info("Monitoring Dashboard Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Dashboard Service: {e}")
            raise

    async def get_system_status_dict(self) -> Dict[str, Any]:
        """_DICT: Holt den System-Status über die Collectors"""
        if not self.initialized:
            await self.initialize()
            
        try:
            system_data = await self.system_collector.collect_system_metrics()
            service_data = await self.service_collector.collect_service_metrics()
            
            # Kombiniere die Listen, wenn vorhanden
            result = []
            
            if isinstance(system_data, list):
                result.extend(system_data)
            elif isinstance(system_data, dict):
                return system_data  # Wenn bereits ein Dict, gib es direkt zurück
                
            if isinstance(service_data, list):
                result.extend(service_data)
            elif isinstance(service_data, dict) and not result:
                return service_data  # Wenn bereits ein Dict und keine Liste existiert
                
            return result
        
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}", exc_info=True)
            return {}
        
    def _extract_ports(self, status_text):
        """Extract port numbers from status text"""
        ports = []
        if 'Port' in status_text:
            try:
                port_section = status_text.split('Port')[1].split(':')[1].strip()
                ports = [int(p.strip()) for p in port_section.split(',') if p.strip().isdigit()]
            except (IndexError, ValueError):
                pass
        return ports

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
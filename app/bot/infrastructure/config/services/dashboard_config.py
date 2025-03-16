from typing import Dict
from app.bot.application.services.dashboard.project_dashboard_service import ProjectDashboardService
from app.bot.application.services.dashboard.monitoring_dashboard_service import MonitoringDashboardService
from app.bot.application.services.dashboard.welcome_dashboard_service import WelcomeDashboardService
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardConfig:
    @staticmethod
    def register(bot) -> Dict:
        dashboard_services = {
            'project': ProjectDashboardService(bot),
            'monitoring': MonitoringDashboardService(bot),
            'welcome': WelcomeDashboardService(bot)
        }
        
        async def setup(bot):
            try:
                for name, service in dashboard_services.items():
                    # Service initialisieren
                    await service.initialize()
                    # Als Service registrieren
                    setattr(bot, f"{name}_dashboard_service", service)
                    # Als Cog registrieren
                    bot.add_cog(service)
                    
                logger.info("Dashboard services initialized")
                return dashboard_services
            except Exception as e:
                logger.error(f"Failed to setup dashboard services: {e}")
                raise
        
        return {
            "name": "Dashboard Services",
            "setup": setup
        }
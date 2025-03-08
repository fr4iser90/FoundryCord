from typing import Dict
from application.services.project_dashboard_service import ProjectDashboardService
from infrastructure.logging import logger

class DashboardConfig:
    @staticmethod
    def register(bot) -> Dict:
        # Erstelle den Service mit bot Parameter
        dashboard_service = ProjectDashboardService(bot)
        
        async def setup(bot):
            try:
                # Initialisiere den Service
                await dashboard_service.initialize()
                
                # Als Cog UND als Service registrieren
                bot.add_cog(dashboard_service)
                setattr(bot, 'project_dashboard_service', dashboard_service)
                
                logger.info("Dashboard service setup completed")
                return dashboard_service
            except Exception as e:
                logger.error(f"Failed to setup dashboard service: {e}")
                raise
        
        return {
            "name": "Project Dashboard",
            "setup": setup,
            "service": dashboard_service
        }
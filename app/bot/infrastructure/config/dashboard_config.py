from typing import Dict, Any
from infrastructure.logging import logger

class DashboardConfig:
    @staticmethod
    def register(bot) -> Dict[str, Any]:
        """Registriert alle Dashboards"""
        async def setup(bot):
            try:
                logger.debug("Starting dashboards setup in DashboardConfig")
                dashboards = {}
                
                # Project Dashboard
                project_result = await bot.dashboard_factory.create('project')
                if project_result:
                    project_dashboard = project_result['dashboard']
                    dashboards['project'] = project_dashboard
                    await project_dashboard.setup()
                
                # General Dashboard
                general_result = await bot.dashboard_factory.create('general')
                if general_result:
                    general_dashboard = general_result['dashboard']
                    dashboards['general'] = general_dashboard
                    await general_dashboard.setup()
                
                return dashboards
                
            except Exception as e:
                logger.error(f"Failed to setup Dashboards: {e}")
                raise
                
        return {
            "name": "Dashboards",
            "setup": setup
        }

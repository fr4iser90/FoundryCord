from typing import Dict, Any
from infrastructure.logging import logger

class DashboardConfig:
    @staticmethod
    def register(bot) -> Dict[str, Any]:
        """Registriert das Project Dashboard"""
        async def setup(bot):
            try:
                logger.debug("Starting dashboard setup in DashboardConfig")
                dashboard_result = bot.dashboard_factory.create('project')
                
                if not dashboard_result:
                    logger.error("Failed to create dashboard")
                    return None
                
                dashboard = dashboard_result['dashboard']
                await dashboard.setup()
                logger.info("Project Dashboard setup completed")
                return dashboard
                
            except Exception as e:
                logger.error(f"Failed to setup Project Dashboard: {e}")
                raise
                
        return {
            "name": "Project Dashboard",
            "setup": setup
        }

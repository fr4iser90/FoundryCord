from typing import Dict, Any
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardConfig:
    @staticmethod
    def register(bot) -> Dict[str, Any]:
        """Registriert alle Dashboards"""
        async def setup(bot):
            try:
                logger.debug("Starting dashboards setup")
                dashboards = {}
                
                # TODO: Rework dashboard setup.
                logger.warning("Dashboard setup skipped - Static constants removed.")
                
                return dashboards
                
            except Exception as e:
                logger.error(f"Failed to setup Dashboards: {e}")
                raise
                
        return {
            "name": "Dashboards",
            "setup": setup
        }

from typing import Dict, Any
from app.shared.logging import logger
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS

class DashboardConfig:
    @staticmethod
    def register(bot) -> Dict[str, Any]:
        """Registriert alle Dashboards"""
        async def setup(bot):
            try:
                logger.debug("Starting dashboards setup")
                dashboards = {}
                
                # Setup all configured dashboards
                for channel_name, config in DASHBOARD_MAPPINGS.items():
                    if config['auto_create']:
                        try:
                            dashboard = await bot.dashboard_factory.create(
                                config['dashboard_type'],
                                channel_name=channel_name,
                                refresh_interval=config['refresh_interval']
                            )
                            if dashboard:
                                dashboards[channel_name] = dashboard['dashboard']
                                await dashboard['dashboard'].setup()
                        except Exception as e:
                            logger.error(f"Failed to setup dashboard for {channel_name}: {e}")
                
                return dashboards
                
            except Exception as e:
                logger.error(f"Failed to setup Dashboards: {e}")
                raise
                
        return {
            "name": "Dashboards",
            "setup": setup
        }

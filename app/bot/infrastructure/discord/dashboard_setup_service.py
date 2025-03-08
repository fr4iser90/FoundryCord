from infrastructure.logging import logger
from infrastructure.config.constants.channel_constants import DASHBOARD_MAPPINGS

class DashboardSetupService:
    def __init__(self, bot):
        self.bot = bot

    async def setup_dashboards(self):
        """Setup all dashboards after channels are ready"""
        try:
            for channel_name, config in DASHBOARD_MAPPINGS.items():
                if config['auto_create']:
                    channel_id = await self.bot.channel_setup.get_channel_id(channel_name)
                    if channel_id:
                        dashboard = await self.bot.dashboard_factory.create(
                            config['dashboard_type'],
                            channel_id=channel_id,
                            refresh_interval=config['refresh_interval']
                        )
                        if dashboard:
                            await dashboard['dashboard'].setup()
                            
        except Exception as e:
            logger.error(f"Dashboard setup failed: {e}")
            raise
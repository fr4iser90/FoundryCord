from .base_workflow import BaseWorkflow
from infrastructure.logging import logger
from infrastructure.config.constants.channel_constants import CHANNELS

class ChannelWorkflow(BaseWorkflow):
    async def initialize(self):
        try:
            logger.debug("Starting channel workflow initialization")
            
            # Create channel setup through factory (similar to service pattern)
            channel_setup = self.bot.factory.create_service(
                "Channel Setup",
                self.bot.channel_config['setup']
            )
            
            # Initialize using lifecycle manager's service initializer
            await self.bot.lifecycle._initialize_service(channel_setup)
            self.bot.channel_setup = channel_setup
            
            return channel_setup
            
        except Exception as e:
            logger.error(f"Channel workflow initialization failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup channel resources"""
        try:
            if self.bot.channel_setup:
                await self.bot.channel_setup.cleanup()
        except Exception as e:
            logger.error(f"Channel cleanup failed: {e}")

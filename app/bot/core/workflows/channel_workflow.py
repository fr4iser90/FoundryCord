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
            
            # Add channel integrity check
            await self._verify_channel_integrity()

            return channel_setup
            
        except Exception as e:
            logger.error(f"Channel workflow initialization failed: {e}")
            raise
            
    async def _verify_channel_integrity(self):
        """Verify all channels exist and repair if needed"""
        try:
            from infrastructure.config.channel_config import ChannelConfig
            from infrastructure.config.constants.channel_constants import CHANNELS
            
            logger.info("Verifying channel integrity...")
            missing_channels = []
            
            # Check all configured channels
            for channel_name in CHANNELS.keys():
                if not await ChannelConfig.validate_channel_id(channel_name, self.bot):
                    missing_channels.append(channel_name)
            
            if missing_channels:
                logger.warning(f"Found {len(missing_channels)} missing channels: {missing_channels}")
                
                # Attempt to repair each missing channel
                for channel_name in missing_channels:
                    repaired = await ChannelConfig.repair_channel_mapping(channel_name, self.bot)
                    if repaired:
                        logger.info(f"Successfully repaired channel: {channel_name}")
                    else:
                        logger.error(f"Failed to repair channel: {channel_name}")
            else:
                logger.info("All channels are intact")
                
        except Exception as e:
            logger.error(f"Channel integrity verification failed: {e}")
            
    async def cleanup(self):
        """Cleanup channel resources"""
        try:
            if self.bot.channel_setup:
                await self.bot.channel_setup.cleanup()
        except Exception as e:
            logger.error(f"Channel cleanup failed: {e}")

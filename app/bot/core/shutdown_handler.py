import asyncio
import signal
import sys
from app.shared.logging import logger

class ShutdownHandler:
    def __init__(self, bot):
        self.bot = bot
        self.is_shutting_down = False
        
    def setup(self):
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigint)
        logger.info("Shutdown handlers registered")
        
    def _handle_sigterm(self, sig, frame):
        """Handle Docker's SIGTERM signal"""
        logger.info("Received SIGTERM signal, starting graceful shutdown...")
        if not self.is_shutting_down:
            self.is_shutting_down = True
            asyncio.create_task(self._shutdown())
    
    def _handle_sigint(self, sig, frame):
        """Handle keyboard interrupt (Ctrl+C)"""
        logger.info("Received SIGINT signal, starting graceful shutdown...")
        if not self.is_shutting_down:
            self.is_shutting_down = True
            asyncio.create_task(self._shutdown())
    
    async def _shutdown(self):
        """Execute graceful shutdown sequence"""
        try:
            logger.info("Starting bot cleanup process...")
            
            # 1. Save all current channel and category data to DB
            logger.info("Saving channel and category data to database...")
            await self._save_channel_data()
            
            # 2. Clean up Discord resources if configured
            if getattr(self.bot.env_config, 'cleanup_on_shutdown', False):
                logger.info("Performing Discord cleanup...")
                await self._cleanup_discord_resources()
            
            # 3. Close connections
            await self.bot.close()
            
            logger.info("Shutdown complete, exiting process")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            sys.exit(1)
    
    async def _save_channel_data(self):
        """Save all channel and category mappings to database"""
        try:
            # Save channel mappings
            if hasattr(self.bot, 'channel_config'):
                channels = await self.bot.channel_config.validate_channels()
                logger.info(f"Verified {len(channels)} channel mappings in database")
            
            # Save category mappings
            if hasattr(self.bot, 'category_setup'):
                # Force save all category mappings
                for category_type, category in self.bot.category_setup.categories.items():
                    if category and hasattr(category, 'id'):
                        await self.bot.category_setup._store_category_mapping(
                            category.id, category_type
                        )
            
            logger.info("Channel and category data saved to database")
        except Exception as e:
            logger.error(f"Error saving channel/category data: {e}")
    
    async def _cleanup_discord_resources(self):
        """Clean up Discord channels and categories if configured"""
        try:
            # Get primary guild
            if not self.bot.guilds:
                logger.warning("No guilds available for cleanup")
                return
                
            guild = self.bot.guilds[0]
            logger.info(f"Starting cleanup in guild: {guild.name}")
            
            # 1. First clean up dashboard messages
            if hasattr(self.bot, 'dashboard_manager'):
                try:
                    dashboard_channels = await self.bot.dashboard_manager.get_dashboard_channels()
                    await self.bot.dashboard_manager.cleanup_old_dashboards(guild, dashboard_channels)
                    logger.info("Dashboard messages cleaned up")
                except Exception as e:
                    logger.error(f"Error cleaning up dashboards: {e}")
            
            # 2. Only delete channels if explicitly configured (safety measure)
            if getattr(self.bot.env_config, 'delete_channels_on_shutdown', False):
                # Get channel names to delete from the configuration
                from app.bot.infrastructure.config.constants.channel_constants import CHANNELS
                
                for channel_name in CHANNELS.keys():
                    try:
                        channel_id = await self.bot.channel_config.get_channel_id(channel_name)
                        if channel_id:
                            channel = self.bot.get_channel(channel_id)
                            if channel:
                                await channel.delete(reason="Bot shutdown cleanup")
                                logger.info(f"Deleted channel: {channel.name}")
                    except Exception as e:
                        logger.error(f"Error deleting channel {channel_name}: {e}")
            
            # 3. Only delete categories if explicitly configured (safety measure)
            if getattr(self.bot.env_config, 'delete_categories_on_shutdown', False):
                # Get category data
                if hasattr(self.bot, 'category_setup'):
                    for category_type, category in self.bot.category_setup.categories.items():
                        if category:
                            try:
                                await category.delete(reason="Bot shutdown cleanup")
                                logger.info(f"Deleted category: {category.name}")
                            except Exception as e:
                                logger.error(f"Error deleting category {category.name}: {e}")
            
            logger.info("Discord resources cleaned up")
        except Exception as e:
            logger.error(f"Error during Discord cleanup: {e}")
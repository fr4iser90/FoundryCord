from typing import Dict, Optional
from nextcord import TextChannel, Guild
from infrastructure.logging import logger
from infrastructure.factories.discord import ChannelFactory, ThreadFactory
import asyncio

class ChannelSetupService:
    def __init__(self, bot):
        self.bot = bot
        self.guild: Optional[Guild] = None
        self.channel_factory = ChannelFactory(bot)
        self.thread_factory = ThreadFactory(bot)
        
    async def initialize(self):
        """Initialize the channel setup service"""
        # Warte bis der Bot bereit ist
        if not self.bot.is_ready():
            logger.info("Waiting for bot to be ready...")
            await self.bot.wait_until_ready()
            
        # Versuche mehrmals die Guild zu bekommen
        retries = 3
        for attempt in range(retries):
            self.guild = self.bot.get_guild(self.bot.env_config.guild_id)
            if self.guild:
                break
            logger.warning(f"Guild not found, attempt {attempt + 1}/{retries}")
            await asyncio.sleep(1)
            
        if not self.guild:
            raise ValueError(f"Guild with ID {self.bot.env_config.guild_id} not found after {retries} attempts")
            
        logger.info(f"Successfully connected to guild: {self.guild.name}")
        return self
        
    async def setup(self):
        """Setup all channels according to config"""
        from infrastructure.config.channel_config import ChannelConfig
        
        try:
            if not self.guild:
                await self.initialize()
                
            for channel_name, config in ChannelConfig.CHANNELS.items():
                logger.info(f"Setting up channel: {channel_name}")
                
                channel_result = self.channel_factory.create(
                    **ChannelConfig.get_channel_factory_config(channel_name, self.guild)
                )
                channel = await channel_result['channel']
                
                # Speichere Channel-ID
                await ChannelConfig.set_channel_id(channel_name, channel.id)
                
                if 'threads' in config:
                    for thread_config in config['threads']:
                        thread_result = self.thread_factory.create(
                            **ChannelConfig.get_thread_factory_config(channel, thread_config['name'])
                        )
                        thread = await thread_result['thread']
                        
                        # Speichere Thread-ID
                        thread_name = f"{channel_name}.{thread_config['name']}"
                        await ChannelConfig.set_channel_id(thread_name, thread.id)
                            
            logger.info("Channel setup completed successfully")
            
        except Exception as e:
            logger.error(f"Channel setup failed: {e}")
            raise 
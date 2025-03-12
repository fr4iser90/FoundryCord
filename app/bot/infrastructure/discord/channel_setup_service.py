from typing import Dict, Optional
from nextcord import TextChannel, Guild
from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.factories.discord import ChannelFactory, ThreadFactory
from app.bot.infrastructure.config.constants.channel_constants import CHANNELS
import asyncio

class ChannelSetupService:
    def __init__(self, bot):
        self.bot = bot
        self.guild: Optional[Guild] = None
        self.channel_factory = ChannelFactory(bot)
        self.thread_factory = ThreadFactory(bot)
        
    async def initialize(self):
        """Initialize service with guild"""
        if not self.bot.guilds:
            raise ValueError("Bot is not connected to any guilds")
        self.guild = self.bot.guilds[0]
        logger.info(f"Successfully connected to guild: {self.guild.name}")
        
    async def setup(self):
        """Setup all channels and their threads"""
        try:
            if not self.guild:
                await self.initialize()
                
            for channel_name, config in CHANNELS.items():
                logger.info(f"Setting up channel: {channel_name}")
                
                # Channel-Konfiguration bereinigen
                channel_config = config.copy()
                channel_config.pop('name', None)
                threads = channel_config.pop('threads', [])  # Threads separat speichern
                
                # Channel erstellen
                channel = await self.channel_factory.create_channel(
                    guild=self.guild,
                    name=channel_name,
                    **channel_config
                )
                
                # Threads für den Channel erstellen
                if channel and threads:
                    for thread_config in threads:
                        thread_name = thread_config.pop('name')  # Name separat
                        await self.thread_factory.create_thread(
                            channel=channel,
                            name=thread_name,
                            **thread_config
                        )
            
            logger.info("Channel setup completed")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise 
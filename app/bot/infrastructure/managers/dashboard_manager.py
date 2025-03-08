# app/bot/infrastructure/managers/dashboard_manager.py
import asyncio
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class DashboardManager:
    def __init__(self, bot):
        self.bot = bot
        
    async def get_dashboard_channels(self) -> List[str]:
        """Holt die Dashboard-Kanäle dynamisch aus der Konfiguration"""
        try:
            from infrastructure.config.channel_config import ChannelConfig
            
            # Alle verfügbaren Kanäle aus der Datenbank holen
            channels = await ChannelConfig.get_dashboard_channels()
            
            # Alle Kanäle zurückgeben, die in der Datenbank existieren
            return list(channels.keys())
            
        except Exception as e:
            logger.error(f"Error getting dashboard channels: {e}")
            return []
        
    async def cleanup_old_dashboards(self, guild, channel_names: Optional[List[str]] = None):
        """Löscht alte Dashboard-Nachrichten in den angegebenen Kanälen"""
        try:
            logger.info("Cleaning up old dashboard messages")
            
            # Wenn keine Kanäle angegeben wurden, hole sie aus der Konfiguration
            if not channel_names:
                channel_names = await self.get_dashboard_channels()
                
            if not channel_names:
                logger.warning("No dashboard channels found in configuration")
                return
            
            for channel_name in channel_names:
                # Kanal-ID aus der Config holen
                from infrastructure.config.channel_config import ChannelConfig
                channel_id = await ChannelConfig.get_channel_id(channel_name)
                if not channel_id:
                    continue
                    
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue
                
                # Suche nach Nachrichten vom Bot in den letzten 100 Nachrichten
                async for message in channel.history(limit=100):
                    if message.author.id == self.bot.user.id and message.embeds:
                        # Prüfe, ob es sich um ein Dashboard handelt
                        for embed in message.embeds:
                            if embed.title and ("Dashboard" in embed.title or "Übersicht" in embed.title):
                                await message.delete()
                                logger.debug(f"Deleted old dashboard message {message.id} in {channel_name}")
                                await asyncio.sleep(0.5)
                                
            logger.info("Dashboard cleanup completed")
        except Exception as e:
            logger.error(f"Error during dashboard cleanup: {e}")
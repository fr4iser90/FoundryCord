# app/bot/infrastructure/managers/dashboard_manager.py
import asyncio
import logging
from typing import List, Optional
from app.bot.interfaces.dashboards.controller.base_dashboard import BaseDashboardController
from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.database.models import DashboardMessage
from app.bot.infrastructure.database.models.config import get_session
from sqlalchemy import select
import nextcord

logger = logging.getLogger(__name__)

class DashboardManager:
    def __init__(self, bot):
        self.bot = bot
        self._dashboards = {}
        
    async def get_dashboard_channels(self) -> List[str]:
        """Holt die Dashboard-Kanäle dynamisch aus der Konfiguration"""
        try:
            from app.bot.infrastructure.config.channel_config import ChannelConfig
            
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
                from app.bot.infrastructure.config.channel_config import ChannelConfig
                channel_id = await ChannelConfig.get_channel_id(channel_name)
                if not channel_id:
                    continue
                    
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue
                
                # Hole alle getrackte Nachrichten für diesen Kanal
                tracked_messages = []
                async for session in get_session():
                    result = await session.execute(
                        select(DashboardMessage).where(DashboardMessage.channel_id == channel_id)
                    )
                    tracked_msgs = result.scalars().all()
                    tracked_messages = [msg.message_id for msg in tracked_msgs]
                
                # Suche nach Nachrichten vom Bot in den letzten 100 Nachrichten
                async for message in channel.history(limit=100):
                    # Überspringe getrackte Nachrichten
                    if message.id in tracked_messages:
                        continue
                        
                    if message.author.id == self.bot.user.id and message.embeds:
                        # Lösche alle Bot-Nachrichten mit Embeds, die nicht getrackt sind
                        await message.delete()
                        logger.debug(f"Deleted old dashboard message {message.id} in {channel_name}")
                        await asyncio.sleep(0.5)
                                
            logger.info("Dashboard cleanup completed")
        except Exception as e:
            logger.error(f"Error during dashboard cleanup: {e}")

    def register_dashboard(self, dashboard_type: str, dashboard: BaseDashboardController):
        """Register a dashboard instance"""
        self._dashboards[dashboard_type] = dashboard
        
    def get_dashboard(self, dashboard_type: str) -> Optional[BaseDashboardController]:
        """Get existing dashboard instance"""
        return self._dashboards.get(dashboard_type)
        
    async def track_message(self, dashboard_type: str, message_id: int, channel_id: int):
        """Track a dashboard message in the database"""
        try:
            async for session in get_session():
                # Check if entry exists
                result = await session.execute(
                    select(DashboardMessage).where(DashboardMessage.dashboard_type == dashboard_type)
                )
                dashboard_msg = result.scalars().first()
                
                if dashboard_msg:
                    # Update existing entry
                    dashboard_msg.message_id = message_id
                    dashboard_msg.channel_id = channel_id
                    logger.debug(f"Updated dashboard message record for {dashboard_type}")
                else:
                    # Create new entry
                    dashboard_msg = DashboardMessage(
                        dashboard_type=dashboard_type,
                        message_id=message_id,
                        channel_id=channel_id
                    )
                    session.add(dashboard_msg)
                    logger.debug(f"Created new dashboard message record for {dashboard_type}")
                
                await session.commit()
                logger.info(f"Saved dashboard message for {dashboard_type} to database")
        except Exception as e:
            logger.error(f"Error tracking dashboard message in database: {e}")
        
    async def get_tracked_message(self, dashboard_type: str) -> Optional[nextcord.Message]:
        """Retrieve tracked message from app.bot.database"""
        try:
            async for session in get_session():
                result = await session.execute(
                    select(DashboardMessage).where(DashboardMessage.dashboard_type == dashboard_type)
                )
                dashboard_msg = result.scalars().first()
                
                if not dashboard_msg:
                    logger.debug(f"No database record found for dashboard type: {dashboard_type}")
                    return None
                    
                channel = self.bot.get_channel(dashboard_msg.channel_id)
                if not channel:
                    logger.warning(f"Channel {dashboard_msg.channel_id} not found for dashboard {dashboard_type}")
                    return None
                
                try:
                    return await channel.fetch_message(dashboard_msg.message_id)
                except nextcord.NotFound:
                    logger.warning(f"Message {dashboard_msg.message_id} not found in channel {dashboard_msg.channel_id}")
                    # Clean up stale record
                    await session.delete(dashboard_msg)
                    await session.commit()
                    return None
                except Exception as e:
                    logger.error(f"Error fetching message: {e}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving dashboard message from app.bot.database: {e}")
            return None

    @staticmethod
    async def setup(bot):
        """Setup and attach a dashboard manager to the bot"""
        logger.info("Setting up Dashboard Manager")
        
        # Check if dashboard manager already exists
        if hasattr(bot, 'dashboard_manager'):
            logger.info("Dashboard Manager already exists")
            return bot.dashboard_manager
        
        # Create new dashboard manager and attach to bot
        bot.dashboard_manager = DashboardManager(bot)
        logger.info("Dashboard Manager initialized successfully")
        return bot.dashboard_manager
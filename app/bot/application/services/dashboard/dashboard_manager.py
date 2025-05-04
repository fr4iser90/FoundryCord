# app/bot/infrastructure/managers/dashboard_manager.py
import asyncio
import logging
from typing import List, Optional, Dict, Any, Callable
from app.bot.interfaces.dashboards.controller import DashboardController
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.infrastructure.models import DashboardMessage
from app.shared.infrastructure.database.core.connection import get_session
from sqlalchemy import select
import nextcord
import importlib
import inspect
import pkgutil
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

class DashboardManager:
    """Manager for registering and activating dashboard types."""
    
    def __init__(self, bot):
        self.bot = bot
        self.dashboard_registry = {}
        self.active_dashboards = {}
        self.initialized = False
        
    def register_dashboard(self, dashboard_type: str, dashboard_class):
        """Register a dashboard type with its class."""
        self.dashboard_registry[dashboard_type] = dashboard_class
        logger.debug(f"Registered dashboard type: {dashboard_type}")
        
    def register_dashboards(self, dashboards: Dict[str, Any]):
        """Register multiple dashboard types at once."""
        for dashboard_type, dashboard_class in dashboards.items():
            self.register_dashboard(dashboard_type, dashboard_class)
            
        logger.info(f"Registered {len(dashboards)} dashboard types")
        
    async def discover_dashboards(self):
        """Discover and register dashboard classes from the dashboards directory."""
        try:
            # Use the new dynamic dashboard system
            self.initialized = True
            logger.info(f"Dashboard Manager initialized")
            return len(self.dashboard_registry)
            
        except Exception as e:
            logger.error(f"Error discovering dashboards: {e}")
            return 0
            
    async def activate_dashboard(self, dashboard_type: str, channel_id: int, **kwargs):
        """Activate a dashboard in a channel."""
        try:
            if dashboard_type not in self.dashboard_registry:
                logger.error(f"Dashboard type not registered: {dashboard_type}")
                return None
                
            # Get channel
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel not found: {channel_id}")
                return None
                
            # Create dashboard instance
            dashboard_class = self.dashboard_registry[dashboard_type]
            dashboard = dashboard_class(self.bot, channel)
            
            # Pass any additional kwargs to initialize
            await dashboard.initialize(**kwargs)
            
            # Store in active dashboards
            self.active_dashboards[channel_id] = dashboard
            
            logger.info(f"Activated {dashboard_type} dashboard in channel {channel.name}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error activating dashboard: {e}")
            return None
            
    async def deactivate_dashboard(self, channel_id: int):
        """Deactivate a dashboard in a channel."""
        try:
            if channel_id not in self.active_dashboards:
                logger.warning(f"No active dashboard in channel: {channel_id}")
                return False
                
            dashboard = self.active_dashboards[channel_id]
            
            # Cleanup dashboard
            await dashboard.cleanup()
            
            # Remove from active dashboards
            del self.active_dashboards[channel_id]
            
            logger.info(f"Deactivated dashboard in channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating dashboard: {e}")
            return False
            
    def get_dashboard(self, channel_id: int):
        """Get the active dashboard in a channel."""
        return self.active_dashboards.get(channel_id)
        
    async def get_dashboard_channels(self) -> List[int]:
        """Get list of channels with active dashboards."""
        return list(self.active_dashboards.keys())
        
    async def refresh_dashboard(self, channel_id: int) -> bool:
        """Refresh a dashboard by channel ID."""
        try:
            if channel_id not in self.active_dashboards:
                logger.warning(f"No active dashboard in channel {channel_id}")
                return False
                
            controller = self.active_dashboards[channel_id]
            await controller.refresh_data()
            await controller.display_dashboard()
            
            logger.debug(f"Refreshed dashboard in channel {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            return False
            
    async def refresh_all_dashboards(self) -> int:
        """Refresh all active dashboards."""
        refreshed = 0
        # This logic is now moved to DashboardRegistry
        logger.warning("refresh_all_dashboards called on DashboardManager, but logic is moved to DashboardRegistry.")
        # Keep the basic structure for potential direct calls, but it won't loop
        for channel_id in list(self.active_dashboards.keys()): # Use list for safety
            if await self.refresh_dashboard(channel_id):
                refreshed += 1
        return refreshed

    async def cleanup_old_dashboards(self, guild, dashboard_channels=None) -> int:
        """Clean up old dashboard messages from specified channels."""
        if dashboard_channels is None:
            dashboard_channels = await self.get_dashboard_channels()
            
        cleaned = 0
        bot_id = self.bot.user.id
        
        for channel_id in dashboard_channels:
            channel = guild.get_channel(channel_id)
            if not channel:
                continue
                
            try:
                # Get all messages by the bot
                async for message in channel.history(limit=100):
                    if message.author.id == bot_id:
                        # Check if it's a dashboard message
                        if message.embeds and any(embed.title for embed in message.embeds):
                            await message.delete()
                            cleaned += 1
                            await asyncio.sleep(0.5)  # Rate limit protection
            except Exception as e:
                logger.error(f"Error cleaning up channel {channel_id}: {e}")
                
        logger.info(f"Cleaned up {cleaned} old dashboard messages")
        return cleaned

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
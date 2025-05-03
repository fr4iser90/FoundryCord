# app/bot/application/services/discord/discord_query_service.py
import nextcord
from typing import Dict, Any, List, Optional

from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class DiscordQueryService:
    """Service to query and structure live data from Discord guilds."""

    def __init__(self, bot):
        self.bot = bot
        logger.info("DiscordQueryService initialized.")

    async def get_live_guild_structure(self, guild: nextcord.Guild) -> Dict[str, Dict[int, Dict[str, Any]]]:
        """Fetches the current category and channel structure from a Discord guild.

        Args:
            guild: The nextcord.Guild object to query.

        Returns:
            A dictionary containing structured data:
            {
                'categories': { category_id: { 'name': ..., 'position': ... } },
                'channels': { channel_id: { 'name': ..., 'type': ..., 'position': ..., 'topic': ..., 'parent_id': ... } }
            }
        """
        logger.debug(f"Fetching live structure for guild: {guild.name} ({guild.id})")
        
        live_categories: Dict[int, Dict[str, Any]] = {}
        live_channels: Dict[int, Dict[str, Any]] = {}

        # Process Categories
        for category in guild.categories:
            live_categories[category.id] = {
                'name': category.name,
                'position': category.position,
                # Add permissions if needed in the future
                # 'permissions': {role.id: overwrite.pair() for target, overwrite in category.overwrites.items() if isinstance(target, nextcord.Role)}
            }

        # Process Channels (excluding categories)
        for channel in guild.channels:
            if isinstance(channel, nextcord.CategoryChannel):
                continue # Skip categories themselves
            
            channel_data = {
                'id': channel.id,
                'name': channel.name,
                'type': str(channel.type), # Store type as string
                'position': channel.position,
                'parent_id': channel.category_id, # Will be None if not in a category
                'topic': getattr(channel, 'topic', None),
                'is_nsfw': getattr(channel, 'nsfw', False),
                'slowmode_delay': getattr(channel, 'slowmode_delay', 0) if isinstance(channel, (nextcord.TextChannel, nextcord.ForumChannel)) else 0,
                 # Add permissions if needed in the future
                # 'permissions': {role.id: overwrite.pair() for target, overwrite in channel.overwrites.items() if isinstance(target, nextcord.Role)}
            }
            # --- ADD LOGGING ---
            logger.debug(f"    QueryService: Processing channel '{channel.name}' (ID: {channel.id}, Type: {channel.type}). Assigning to live_channels.")
            # --- END LOGGING ---
            live_channels[channel.id] = channel_data
            
        logger.debug(f"Fetched {len(live_categories)} categories and {len(live_channels)} channels for guild {guild.id}")

        live_structure = {
            'categories': live_categories,
            'channels': live_channels
        }

        return live_structure

# Example of how it might be instantiated or accessed
# Needs integration with the bot's service management/factory pattern if one exists. 
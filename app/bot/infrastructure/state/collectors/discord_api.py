"""Collectors related to Discord API state."""
from typing import Dict, Any
import nextcord
from app.shared.interface.logging.api import get_shared_logger

logger = get_shared_logger()

def collect_discord_connection_info_func(bot: nextcord.Client) -> Dict[str, Any]:
    """
    Collects Discord connection information from the bot instance.
    
    Args:
        bot: The Discord bot instance.
        
    Returns:
        Dict with Discord connection info.
    """
    logger.debug("Executing discord_connection state collector...")
    if not bot or not hasattr(bot, 'latency'):
        # Check if bot is None or doesn't have the latency attribute yet (not connected)
        return {"error": "Bot not available or not connected to Discord Gateway"}
            
    try:    
        return {
            "latency_ms": round(bot.latency * 1000, 2) if bot.latency else None,
            "is_closed": bot.is_closed() if hasattr(bot, 'is_closed') else None,
            "is_ready": bot.is_ready() if hasattr(bot, 'is_ready') else None,
            "shard_count": bot.shard_count if hasattr(bot, 'shard_count') else None,
            "user": str(bot.user) if bot.user else None,
            "intents": str(bot.intents) if hasattr(bot, 'intents') else None
            # Removed ws_ratelimit as it's likely internal/less useful
        }
    except Exception as e:
        logger.error(f"Error collecting Discord connection info: {e}", exc_info=True)
        return {"error": str(e)}

def collect_guilds_summary_func(bot: nextcord.Client) -> Dict[str, Any]:
    """
    Collects summary of Discord guilds/servers from the bot instance.
    
    Args:
        bot: The Discord bot instance.
        
    Returns:
        Dict with guild summary information.
    """
    logger.debug("Executing discord_guilds_summary state collector...")
    if not bot or not hasattr(bot, 'guilds'):
        return {"error": "Bot not available or guilds not cached"}
        
    try:    
        guilds = bot.guilds
        guild_count = len(guilds)
        
        if guild_count == 0:
            return {
                "guild_count": 0,
                "member_count_total": 0
            }
            
        member_counts = [g.member_count for g in guilds if g.member_count is not None] # Filter out None if large guilds unavailable
        channel_counts = [len(g.channels) for g in guilds]
        role_counts = [len(g.roles) for g in guilds]
        
        total_members = sum(member_counts)
        
        return {
            "guild_count": guild_count,
            "member_count_total": total_members,
            "averages": {
                "members_per_guild": round(total_members / guild_count, 2),
                "channels_per_guild": round(sum(channel_counts) / guild_count, 2),
                "roles_per_guild": round(sum(role_counts) / guild_count, 2)
            },
            "largest_guild_size": max(member_counts) if member_counts else 0,
            "smallest_guild_size": min(member_counts) if member_counts else 0
        }
    except Exception as e:
        logger.error(f"Error collecting Discord guilds summary: {e}", exc_info=True)
        return {"error": str(e)}

def collect_commands_info_func(bot: nextcord.Client) -> Dict[str, Any]:
    """
    Collects information about registered commands from the bot instance.
    
    Args:
        bot: The Discord bot instance.
        
    Returns:
        Dict with command information.
    """
    logger.debug("Executing discord_commands state collector...")
    if not bot:
        return {"error": "Bot instance not provided"}
        
    try:
        app_commands = []
        if hasattr(bot, 'tree') and hasattr(bot.tree, 'get_commands'):
            # tree.get_commands() might include sub-commands, depending on framework version
            # We might want to flatten or just count top-level commands
            try: 
                app_commands = bot.tree.get_commands()
            except Exception as tree_err:
                logger.warning(f"Could not get app commands from tree: {tree_err}")
                app_commands = []
            
        traditional_commands = list(bot.commands) if hasattr(bot, 'commands') else []
        
        # Helper to get categories from traditional commands
        categories = {}
        for cmd in traditional_commands:
            category = getattr(cmd, 'cog_name', 'Uncategorized') # Use cog name as category
            categories[category] = categories.get(category, 0) + 1
            
        return {
            "traditional_commands_count": len(traditional_commands),
            "traditional_command_names": sorted([cmd.qualified_name for cmd in traditional_commands]),
            "app_commands_count": len(app_commands),
            "app_command_names": sorted([cmd.name for cmd in app_commands]),
            "command_categories": categories
        }
    except Exception as e:
        logger.error(f"Error collecting Discord commands info: {e}", exc_info=True)
        return {"error": str(e)} 
"""
Bot State Collectors - Implements state collection for the Discord bot runtime
"""
from typing import Dict, Any, List, Optional, Callable
import nextcord
import logging
import time
import psutil
import platform
import sys
import asyncio
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service

# Configure logger
logger = logging.getLogger("homelab.bot")

class BotStateCollectors:
    """
    Provides bot-specific state collectors for capturing runtime state
    """
    
    def __init__(self, bot):
        """
        Initialize with reference to the bot instance
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.snapshot_service = get_state_snapshot_service()
        self.initialized = False
        
    async def initialize(self):
        """
        Register all bot state collectors with the snapshot service
        """
        if self.initialized:
            logger.debug("Bot state collectors already initialized")
            return
            
        # Basic bot state collectors (require no special permissions)
        self.snapshot_service.register_collector(
            name="bot_basic_info",
            collector_fn=self.collect_basic_info,
            requires_approval=False,
            scope="bot",
            description="Basic bot status and version information"
        )
        
        self.snapshot_service.register_collector(
            name="bot_system_info",
            collector_fn=self.collect_system_info,
            requires_approval=False,
            scope="bot",
            description="Bot host system information"
        )
        
        self.snapshot_service.register_collector(
            name="bot_performance",
            collector_fn=self.collect_performance_metrics,
            requires_approval=False,
            scope="bot",
            description="Bot performance metrics"
        )
        
        # Discord-specific state collectors (require approval)
        self.snapshot_service.register_collector(
            name="discord_connection",
            collector_fn=self.collect_discord_connection_info,
            requires_approval=True,
            scope="bot",
            description="Discord connection and gateway information"
        )
        
        self.snapshot_service.register_collector(
            name="discord_guilds_summary",
            collector_fn=self.collect_guilds_summary,
            requires_approval=True,
            scope="bot",
            description="Summary of connected Discord servers/guilds"
        )
        
        self.snapshot_service.register_collector(
            name="discord_commands",
            collector_fn=self.collect_commands_info,
            requires_approval=True,
            scope="bot",
            description="Registered Discord commands information"
        )
        
        # Advanced state collectors (always require approval)
        self.snapshot_service.register_collector(
            name="database_connection",
            collector_fn=self.collect_database_connection_info,
            requires_approval=True,
            scope="bot",
            description="Database connection status (no sensitive data)"
        )
        
        self.snapshot_service.register_collector(
            name="active_listeners",
            collector_fn=self.collect_active_listeners,
            requires_approval=True,
            scope="bot",
            description="Currently active event listeners"
        )
        
        self.snapshot_service.register_collector(
            name="cog_status",
            collector_fn=self.collect_cog_status,
            requires_approval=True,
            scope="bot",
            description="Status of loaded cogs/extensions"
        )
        
        self.initialized = True
        logger.info("Bot state collectors initialized successfully")
    
    async def collect_basic_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect basic bot information
        
        Returns:
            Dict with basic bot information
        """
        return {
            "uptime": time.time() - self.bot.start_time if hasattr(self.bot, 'start_time') else None,
            "version": getattr(self.bot, 'version', 'unknown'),
            "nextcord_version": nextcord.__version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "environment": getattr(self.bot, 'env_config', {}).get('environment', 'unknown'),
            "is_development": getattr(self.bot, 'env_config', {}).get('is_development', False),
            "lifecycle_state": self.bot.lifecycle.get_state() if hasattr(self.bot, 'lifecycle') else 'unknown'
        }
    
    async def collect_system_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect system information from the bot's host
        
        Returns:
            Dict with system information
        """
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }
    
    async def collect_performance_metrics(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect performance metrics about the bot
        
        Returns:
            Dict with performance metrics
        """
        process = psutil.Process()
        
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_usage": {
                "rss": process.memory_info().rss,  # Resident Set Size
                "vms": process.memory_info().vms,  # Virtual Memory Size
                "percent": process.memory_percent()
            },
            "threads": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections()),
            "system_load": psutil.getloadavg()
        }
    
    async def collect_discord_connection_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect Discord connection information
        
        Returns:
            Dict with Discord connection info
        """
        if not self.bot or not hasattr(self.bot, 'latency'):
            return {"error": "Bot not initialized or connected"}
            
        return {
            "latency": self.bot.latency,
            "is_closed": self.bot.is_closed() if hasattr(self.bot, 'is_closed') else None,
            "is_ready": self.bot.is_ready() if hasattr(self.bot, 'is_ready') else None,
            "shard_count": self.bot.shard_count if hasattr(self.bot, 'shard_count') else None,
            "ws_ratelimit": getattr(self.bot, '_ws_ratelimit', None) if hasattr(self.bot, '_ws_ratelimit') else None,
            "user": str(self.bot.user) if self.bot.user else None,
            "intents": str(self.bot.intents) if hasattr(self.bot, 'intents') else None
        }
    
    async def collect_guilds_summary(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect summary of Discord guilds/servers
        
        Returns:
            Dict with guild summary information
        """
        if not self.bot or not hasattr(self.bot, 'guilds'):
            return {"error": "Bot not initialized or connected"}
            
        guilds = self.bot.guilds
        
        # Don't return specific guild IDs, just count information
        return {
            "guild_count": len(guilds),
            "member_count_total": sum(g.member_count for g in guilds),
            "averages": {
                "members_per_guild": sum(g.member_count for g in guilds) / len(guilds) if guilds else 0,
                "channels_per_guild": sum(len(g.channels) for g in guilds) / len(guilds) if guilds else 0,
                "roles_per_guild": sum(len(g.roles) for g in guilds) / len(guilds) if guilds else 0
            },
            "largest_guild_size": max(g.member_count for g in guilds) if guilds else 0,
            "smallest_guild_size": min(g.member_count for g in guilds) if guilds else 0
        }
    
    async def collect_commands_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect information about registered commands
        
        Returns:
            Dict with command information
        """
        if not self.bot or not hasattr(self.bot, 'commands'):
            return {"error": "Bot not initialized or commands unavailable"}
            
        # For application/slash commands
        app_commands = []
        if hasattr(self.bot, 'tree') and hasattr(self.bot.tree, 'get_commands'):
            app_commands = self.bot.tree.get_commands()
            
        # For traditional commands
        traditional_commands = list(self.bot.commands) if hasattr(self.bot, 'commands') else []
            
        return {
            "traditional_commands_count": len(traditional_commands),
            "traditional_command_names": [cmd.name for cmd in traditional_commands],
            "app_commands_count": len(app_commands),
            "app_command_names": [cmd.name for cmd in app_commands],
            "command_categories": self._get_command_categories()
        }
    
    async def collect_database_connection_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect database connection information
        
        Returns:
            Dict with database connection status (no credentials)
        """
        # Access the database service if available
        db_service = getattr(self.bot, 'db_service', None)
        if not db_service:
            return {"status": "unavailable", "reason": "No database service found"}
            
        is_connected = False
        try:
            # Check if we can execute a simple query
            is_connected = await db_service.ping()
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "is_connected": False
            }
            
        return {
            "status": "connected" if is_connected else "disconnected",
            "is_connected": is_connected,
            "database_type": getattr(db_service, 'db_type', 'unknown'),
            "engine_url": str(db_service.engine.url).replace(
                # Replace any sensitive parts with ***
                db_service.engine.url.password or '', 
                '***'
            ) if hasattr(db_service, 'engine') and hasattr(db_service.engine, 'url') else 'unknown'
        }
    
    async def collect_active_listeners(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect information about active event listeners
        
        Returns:
            Dict with event listener information
        """
        if not self.bot or not hasattr(self.bot, '_listeners'):
            return {"error": "Bot not initialized or listeners unavailable"}
            
        listeners = {}
        
        for event_name, handlers in self.bot._listeners.items():
            listeners[event_name] = len(handlers)
            
        return {
            "event_types": list(listeners.keys()),
            "listener_counts": listeners,
            "total_listeners": sum(listeners.values())
        }
    
    async def collect_cog_status(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect status of loaded cogs/extensions
        
        Returns:
            Dict with cog status information
        """
        if not self.bot or not hasattr(self.bot, 'cogs'):
            return {"error": "Bot not initialized or cogs unavailable"}
            
        cogs = self.bot.cogs
        extensions = list(self.bot.extensions.keys()) if hasattr(self.bot, 'extensions') else []
            
        return {
            "loaded_cogs": list(cogs.keys()),
            "cog_count": len(cogs),
            "loaded_extensions": extensions,
            "extension_count": len(extensions)
        }
    
    def _get_command_categories(self) -> Dict[str, int]:
        """
        Helper to group commands by category
        
        Returns:
            Dict mapping category names to command counts
        """
        categories = {}
        
        if hasattr(self.bot, 'commands'):
            for cmd in self.bot.commands:
                category = getattr(cmd, 'category', 'Uncategorized')
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
                
        return categories


# Create a function to get a configured collector instance
def setup_bot_state_collectors(bot):
    """
    Create and initialize bot state collectors
    
    Args:
        bot: The Discord bot instance
        
    Returns:
        Initialized BotStateCollectors instance
    """
    collectors = BotStateCollectors(bot)
    asyncio.create_task(collectors.initialize())
    return collectors 
"""
Bot State Collectors - Implements state collection for the Discord bot runtime
"""
from typing import Dict, Any, List, Optional, Callable
import nextcord
import logging
import time
# Removed platform, psutil, sys, asyncio imports
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service

# Import collector functions
from .collectors.basic_info import collect_basic_info_func
# Import system_info from SHARED infrastructure
from app.shared.infrastructure.state.collectors.system_info import get_system_info as collect_system_info_func
from .collectors.performance import collect_performance_metrics_func
from .collectors.discord_api import (
    collect_discord_connection_info_func, 
    collect_guilds_summary_func, 
    collect_commands_info_func
)
from .collectors.database_status import collect_database_connection_info_func
from .collectors.listeners import collect_active_listeners_func
from .collectors.cog_status import collect_cog_status_func

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
        Register all bot state collectors with the snapshot service.
        The collector functions now point to the methods of this instance,
        which in turn call the refactored functions.
        """
        if self.initialized:
            logger.debug("Bot state collectors already initialized")
            return
            
        # Basic bot state collectors (require no special permissions)
        self.snapshot_service.register_collector(
            name="bot_basic_info",
            collector_fn=self.collect_basic_info, # Register the method
            requires_approval=False,
            scope="bot",
            description="Basic bot status and version information"
        )
        
        self.snapshot_service.register_collector(
            name="bot_system_info",
            collector_fn=self.collect_system_info, # Still register the method wrapper
            requires_approval=False,
            scope="bot",
            description="Bot host system information (uses shared collector logic)" # Updated description
        )
        
        self.snapshot_service.register_collector(
            name="bot_performance",
            collector_fn=self.collect_performance_metrics, # Register the method
            requires_approval=False,
            scope="bot",
            description="Bot performance metrics"
        )
        
        # Discord-specific state collectors (require approval)
        self.snapshot_service.register_collector(
            name="discord_connection",
            collector_fn=self.collect_discord_connection_info, # Register the method
            requires_approval=True,
            scope="bot",
            description="Discord connection and gateway information"
        )
        
        self.snapshot_service.register_collector(
            name="discord_guilds_summary",
            collector_fn=self.collect_guilds_summary, # Register the method
            requires_approval=True,
            scope="bot",
            description="Summary of connected Discord servers/guilds"
        )
        
        self.snapshot_service.register_collector(
            name="discord_commands",
            collector_fn=self.collect_commands_info, # Register the method
            requires_approval=True,
            scope="bot",
            description="Registered Discord commands information"
        )
        
        # Advanced state collectors (always require approval)
        self.snapshot_service.register_collector(
            name="database_connection",
            collector_fn=self.collect_database_connection_info, # Register the method
            requires_approval=True,
            scope="bot",
            description="Database connection status (from bot's perspective)"
        )
        
        self.snapshot_service.register_collector(
            name="active_listeners",
            collector_fn=self.collect_active_listeners, # Register the method
            requires_approval=True,
            scope="bot",
            description="Currently active event listeners"
        )
        
        self.snapshot_service.register_collector(
            name="cog_status",
            collector_fn=self.collect_cog_status, # Register the method
            requires_approval=True,
            scope="bot",
            description="Status of loaded cogs/extensions"
        )
        
        self.initialized = True
        logger.info("Bot state collectors initialized successfully")
    
    # --- Collector Methods (now wrappers) ---
    
    async def collect_basic_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect basic bot information by calling the refactored function."""
        # Context is not used by the underlying function, but kept for signature consistency
        return collect_basic_info_func(self.bot)
    
    async def collect_system_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect system information by calling the SHARED refactored function."""
        # Context is not used by the underlying function
        # Call the imported function directly
        return await collect_system_info_func() # Use await as the shared function is async
    
    async def collect_performance_metrics(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect performance metrics by calling the refactored function."""
        # Context is not used by the underlying function
        # Note: This function is now async to match the signature, but the work isn't async
        return collect_performance_metrics_func()
    
    async def collect_discord_connection_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect Discord connection info by calling the refactored function."""
        return collect_discord_connection_info_func(self.bot)
    
    async def collect_guilds_summary(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect guilds summary by calling the refactored function."""
        return collect_guilds_summary_func(self.bot)
    
    async def collect_commands_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect commands info by calling the refactored function."""
        return collect_commands_info_func(self.bot)
    
    async def collect_database_connection_info(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect bot database connection info by calling the refactored function."""
        return await collect_database_connection_info_func(self.bot)
    
    async def collect_active_listeners(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect active listeners info by calling the refactored function."""
        return collect_active_listeners_func(self.bot)
    
    async def collect_cog_status(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect cog status info by calling the refactored function."""
        return collect_cog_status_func(self.bot)
    
    # Removed _get_command_categories as it's now inside discord_api.py (implicitly)

# Keep setup function as it is, it initializes the class which now handles delegation
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
    # The initialize method needs to be awaited if called from async context
    # Or handled appropriately if called from sync context (e.g., asyncio.run)
    # Assuming it's called from an async setup function:
    # await collectors.initialize()
    # If called from sync, needs task creation:
    import asyncio
    try:
        asyncio.create_task(collectors.initialize())
    except RuntimeError as e:
        # Handle cases where event loop might not be running yet (e.g. very early startup)
        logger.warning(f"Could not create task for BotStateCollectors init (may happen if loop not running): {e}")
        # Attempt to run synchronously if possible (use with caution)
        # try:
        #     asyncio.run(collectors.initialize())
        # except RuntimeError:
        #     logger.error("Failed to run BotStateCollectors initialize synchronously.")
            
    return collectors 
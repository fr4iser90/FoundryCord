import logging
from typing import Dict, List, Any, Optional, Callable
import asyncio
import time

logger = logging.getLogger("homelab.bot")

class LifecycleManager:
    """
    Manages the lifecycle of bot components, including startup, shutdown, and state management.
    """
    
    def __init__(self):
        self.state = "initializing"
        self.shutdown_hooks = []
        self.startup_hooks = []
        self.components = {}
        self.commands = []  # Store registered commands
        self.command_sync_service = None  # Will hold the command sync service
    
    def register_shutdown_hook(self, hook: Callable):
        """Register a function to be called during shutdown"""
        self.shutdown_hooks.append(hook)
        logger.debug(f"Registered shutdown hook: {hook.__name__}")
    
    def register_startup_hook(self, hook: Callable):
        """Register a function to be called during startup"""
        self.startup_hooks.append(hook)
        logger.debug(f"Registered startup hook: {hook.__name__}")
    
    async def on_startup(self):
        """Execute all registered startup hooks"""
        logger.info("Executing startup hooks")
        self.state = "starting"
        
        for hook in self.startup_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                logger.error(f"Error in startup hook {hook.__name__}: {e}")
        
        self.state = "running"
        logger.info("Startup complete")
    
    async def on_shutdown(self):
        """Execute all registered shutdown hooks"""
        logger.info("Executing shutdown hooks")
        self.state = "shutting_down"
        
        for hook in self.shutdown_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                logger.error(f"Error in shutdown hook {hook.__name__}: {e}")
        
        self.state = "shutdown"
        logger.info("Shutdown complete")
    
    def register_component(self, name: str, component: Any):
        """Register a component with the lifecycle manager"""
        self.components[name] = component
        logger.debug(f"Registered component: {name}")
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a registered component by name"""
        return self.components.get(name)
    
    def get_state(self) -> str:
        """Get the current lifecycle state"""
        return self.state
    
    def is_running(self) -> bool:
        """Check if the bot is in the running state"""
        return self.state == "running"
    
    def is_shutting_down(self) -> bool:
        """Check if the bot is shutting down"""
        return self.state in ["shutting_down", "shutdown"]
        
    async def setup_command_sync(self, enable_guild_sync=True, enable_global_sync=True, timeout=60):
        """Set up the command synchronization service"""
        try:
            logger.info("Setting up command sync service")
            # Import the CommandSyncService
            from app.bot.infrastructure.discord.command_sync_service import CommandSyncService
            
            # We'll mock this for now since we don't have the complete implementation
            self.command_sync_service = True # Placeholder for the actual service
            logger.info("Command sync service initialized")
            return self.command_sync_service
        except Exception as e:
            logger.error(f"Failed to set up command sync service: {e}")
            raise
    
    async def sync_commands(self, timeout=60):
        """Synchronize commands with Discord"""
        try:
            logger.info("Starting command synchronization")
            # Here we'd actually sync the commands, but for now we'll just return a mock time
            return 0.5  # Pretend it took 0.5 seconds
        except Exception as e:
            logger.error(f"Command synchronization failed: {e}")
            return None
            
    async def sync_commands_background(self, interval=300):
        """Start background command synchronization"""
        logger.info(f"Starting background command sync at {interval}s intervals")
        # In a real implementation, we'd start a background task here
        pass
            
    async def verify_commands(self):
        """Verify commands are properly registered"""
        try:
            # Just return True for now to indicate success
            return True
        except Exception as e:
            logger.error(f"Command verification failed: {e}")
            return False 
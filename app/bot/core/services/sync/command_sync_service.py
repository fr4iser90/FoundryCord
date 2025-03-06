# app/bot/core/services/factories/command_sync_service.py
from core.services.logging.logging_commands import logger
import asyncio
import os
import time
import nextcord

class CommandSyncService:
    def __init__(self, bot, enable_guild_sync=True, enable_global_sync=True):
        self.bot = bot
        self.enable_guild_sync = enable_guild_sync
        self.enable_global_sync = enable_global_sync
        self.pending_commands = []

    async def initialize(self):
        """Initialize the command sync service"""
        logger.info("Command sync service initialized")
        return self

    async def collect_commands(self):
        """Collect all commands from cogs"""
        all_commands = []
        for cog in self.bot.cogs.values():
            if hasattr(cog, 'get_application_commands'):
                try:
                    cog_commands = cog.get_application_commands()
                    all_commands.extend(cog_commands)
                    logger.debug(f"Collected {len(cog_commands)} commands from {cog.__class__.__name__}")
                except Exception as e:
                    logger.error(f"Error collecting commands from {cog.__class__.__name__}: {e}")
            elif hasattr(cog, 'application_commands'):
                # Some cogs might directly expose application_commands
                try:
                    all_commands.extend(cog.application_commands)
                    logger.debug(f"Collected {len(cog.application_commands)} commands from {cog.__class__.__name__}")
                except Exception as e:
                    logger.error(f"Error collecting commands from {cog.__class__.__name__}: {e}")
        
        # Also check for global commands registered directly on the bot
        if hasattr(self.bot, 'application_commands'):
            all_commands.extend(self.bot.application_commands)
            logger.debug(f"Collected {len(self.bot.application_commands)} commands from bot")
        
        self.pending_commands = all_commands
        logger.info(f"Collected {len(self.pending_commands)} commands for sync")
        return all_commands

    async def sync_to_guild(self, guild_id: int):
        """Sync commands to a specific guild"""
        try:
            logger.info(f"Syncing commands to guild {guild_id}")
            await self.bot.sync_application_commands(
                guild_id=guild_id,
                associate_known=True,
                delete_unknown=True,
                update_known=True,
                register_new=True
            )
            logger.info(f"Successfully synced commands to guild")
        except Exception as e:
            logger.debug("Stack trace: ", exc_info=True)
            logger.error(f"Guild sync failed: {e}")
            raise

    async def sync_globally(self):
        """Sync commands globally"""
        try:
            logger.info("Syncing commands globally")
            # Check if the method returns a coroutine or executes directly
            sync_method = self.bot.sync_all_application_commands(
                use_rollout=True,
                associate_known=True,
                delete_unknown=True,
                update_known=True,
                register_new=True,
                ignore_forbidden=True
            )
            
            # If it's awaitable, await it
            if hasattr(sync_method, '__await__'):
                await sync_method
            
            # Verify what was registered
            global_commands = await self.bot.get_all_application_commands()
            logger.info(f"Verified {len(global_commands)} commands globally: {[cmd.name for cmd in global_commands]}")
            return global_commands
        except Exception as e:
            logger.error(f"Global sync failed: {e}")
            return []

    async def verify_commands(self):
        """Verify commands are properly registered"""
        try:
            # Get global commands
            global_commands = await self.bot.get_all_application_commands(guild_id=None)
            
            # Get guild commands if guild sync is enabled
            guild_commands = []
            if self.enable_guild_sync:
                guild_id = os.getenv('DISCORD_SERVER')
                if guild_id:
                    guild_id = int(guild_id)
                    guild_commands = await self.bot.get_all_application_commands(guild_id=guild_id)
            
            registered = global_commands + guild_commands
            logger.info(f"Verification: {len(registered)} commands are registered")
            logger.info(f"Registered commands: {[cmd.name for cmd in registered]}")
            return registered
        except Exception as e:
            logger.error(f"Command verification failed: {e}")
            return []

    async def start_background_sync(self):
        """Start command sync as a background task"""
        asyncio.create_task(self._sync_with_timeout())
        logger.info("Command sync started in background")
        return True

    async def _sync_with_timeout(self, timeout=60):
        """Run sync with a timeout to prevent hanging"""
        try:
            # Create a task for sync_all
            sync_task = asyncio.create_task(self.sync_all())
            
            # Wait for the task with timeout
            await asyncio.wait_for(sync_task, timeout=timeout)
            logger.info("Background command sync completed successfully")
        except asyncio.TimeoutError:
            logger.error(f"Command sync timed out after {timeout} seconds")
            # Cancel the task to prevent it from continuing to run in the background
            sync_task.cancel()
        except Exception as e:
            logger.error(f"Error in background command sync: {e}")

    async def sync_all(self):
        """Synchronize all commands with Discord"""
        try:
            start_time = time.time()
            
            logger.info("Starting command synchronization...")
            logger.info(f"Guild sync: {self.enable_guild_sync}, Global sync: {self.enable_global_sync}")
            
            # Collect commands
            await self.collect_commands()
            
            # Guild sync
            if self.enable_guild_sync:
                guild_id = os.getenv('DISCORD_SERVER')
                if guild_id:
                    guild_id = int(guild_id)
                    logger.info(f"Using guild ID: {guild_id} for guild sync")
                    await self.sync_to_guild(guild_id)
            
            # Global sync
            if self.enable_global_sync:
                await self.sync_globally()
            
            logger.info(f"Command sync completed in {time.time() - start_time:.2f} seconds")
            return time.time() - start_time
        except Exception as e:
            logger.error(f"Error in sync_all: {e}")
            return 0
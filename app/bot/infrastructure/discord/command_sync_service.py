# app/bot/core/services/factories/command_sync_service.py
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
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
        self.background_tasks = []

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
        """Sync commands to a specific guild using get_application_commands to verify"""
        try:
            logger.info(f"Syncing commands to guild {guild_id}")
            
            # Get commands before sync for comparison
            before_commands = await self.bot.get_application_commands(guild_id=guild_id)
            logger.info(f"Before sync: {len(before_commands)} commands exist in guild")
            
            # Sync commands
            await self.bot.sync_application_commands(guild_id=guild_id)
            
            # Verify by getting commands after sync
            after_commands = await self.bot.get_application_commands(guild_id=guild_id)
            logger.info(f"After sync: {len(after_commands)} commands exist in guild")
            logger.info(f"Command names: {[cmd.name for cmd in after_commands]}")
            
            return after_commands
        except Exception as e:
            logger.error(f"Guild sync failed: {e}", exc_info=True)
            raise

    async def sync_globally(self):
        """Sync commands globally"""
        try:
            logger.info("Syncing commands globally")
            
            result = await self.bot.sync_all_application_commands(
                use_rollout=True,
                associate_known=True,
                delete_unknown=True,
                update_known=True,
                register_new=True,
                ignore_forbidden=True
            )
            
            # Log the sync result if it exists
            if result is not None:
                logger.info(f"Sync returned {len(result) if hasattr(result, '__len__') else 'unknown'} commands")
            
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

            
            registered = global_commands + guild_commands
            logger.info(f"Verification: {len(registered)} commands are registered")
            logger.info(f"Registered commands: {[cmd.name for cmd in registered]}")
            return registered
        except Exception as e:
            logger.error(f"Command verification failed: {e}")
            return []

    async def start_background_sync(self, interval=60, timeout=10, initial_delay=10):
        """Start background sync with initial delay to prevent double loading"""
        try:
            # First wait for initial delay to prevent immediate double sync
            if initial_delay > 0:
                logger.info(f"Delaying first background sync by {initial_delay} seconds")
                await asyncio.sleep(initial_delay)
            
            sync_task = asyncio.create_task(self._background_sync_loop(interval, timeout))
            self.background_tasks.append(sync_task)
            logger.info("Command sync started in background")
            return sync_task
        except Exception as e:
            logger.error(f"Failed to start background sync: {e}")
            raise

    async def _background_sync_loop(self, interval, timeout):
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

    async def sync_all(self, force=True):
        """Synchronize all commands with Discord"""
        try:
            start_time = time.time()

            logger.info("Starting command synchronization...")
            logger.info(f"Guild sync: {self.enable_guild_sync}, Global sync: {self.enable_global_sync}")
            
            # Collect commands
            await self.collect_commands()
                        
            # Global sync
            if self.enable_global_sync:
                await self.sync_globally()
            
            # Log time and return
            sync_time = time.time() - start_time
            logger.info(f"Command sync completed in {sync_time:.2f} seconds")
            return sync_time
        except Exception as e:
            logger.error(f"Error in sync_all: {e}", exc_info=True)
            return 0

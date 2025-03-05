from core.services.logging.logging_commands import logger
import asyncio
import time
import os

enable_guild_sync = True
enable_global_sync = True

class BotStartup:
    def __init__(self, bot):
        self.bot = bot
        self.services = []
        self.tasks = []
        self.commands = []
        self.ready_event = asyncio.Event()
        self.pending_commands = []  # NEW: Track commands during registration

    def register_service(self, name, setup_func):
        """Register a service for initialization"""
        self.services.append((name, setup_func))
        logger.debug(f"Service registered: {name}")

    def register_task(self, name, task_func, *args):
        """Register a background task"""
        self.tasks.append((name, task_func, args))
        logger.debug(f"Task registered: {name}")

    def register_command(self, name: str, setup_func):
        """Register a command setup function"""
        self.commands.append((name, setup_func))

    async def initialize_services(self):
        """Initialize all registered services"""
        logger.info("Initializing bot services...")
        
        for name, setup_func in self.services:
            try:
                logger.info(f"Starting initialization of service: {name}")
                await setup_func(self.bot)
                logger.info(f"Completed initialization of service: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize service {name}: {e}")
                raise

    async def wait_until_ready(self, timeout=30):  # Add timeout
        """Wait for all critical services with timeout"""
        logger.info("Waiting for critical services to be ready...")
        try:
            await asyncio.wait_for(self.ready_event.wait(), timeout=timeout)
            logger.info("All critical services are ready")
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for critical services")
            # Continue anyway as services might be partially ready

    async def start_tasks(self):
        """Start registered tasks with logging"""
        logger.info("Starting registered tasks...")
        for name, task_func, args in self.tasks:
            try:
                logger.info(f"Starting task: {name}")
                asyncio.create_task(task_func(self.bot, *args))
                logger.info(f"Task started: {name}")
            except Exception as e:
                logger.error(f"Failed to start task {name}: {e}")

    async def collect_commands(self):
        """Collect all commands before sync"""
        commands = []
        for cog in self.bot.cogs.values():
            commands.extend(cog.application_commands)
        logger.info(f"Collected {len(commands)} commands for sync")
        return commands

    async def verify_commands(self):
        """Verify commands are properly registered"""
        try:
            registered = await self.bot.fetch_application_commands()
            logger.info(f"Verified {len(registered)} commands are registered")
            
            # Log each command for debugging
            for cmd in registered:
                logger.debug(f"Command registered: {cmd.name} ({cmd.id})")
                
            return True
        except Exception as e:
            logger.error(f"Command verification failed: {e}")
            return False

    async def register_commands(self, cog):
        """Track commands during registration"""
        self.pending_commands.extend(cog.application_commands)
        self.bot.add_cog(cog)
        
    async def sync_commands(self, timeout=60, batch_size=5):
        """Synchronize commands with timing measurement, timeout and batch processing"""
        global enable_guild_sync, enable_global_sync
        
        logger.info("Starting command synchronization...")
        logger.info(f"Guild sync: {'ENABLED' if enable_guild_sync else 'DISABLED'}, Global sync: {'ENABLED' if enable_global_sync else 'DISABLED'}")
        start_time = time.time()
        
        try:
            # Collect all commands that will be synced
            commands = await self.collect_commands()
            
            # Log each command being synced
            for cmd in commands:
                logger.info(f"Syncing command: {cmd.name}")
            
            # If no commands, skip sync
            if not commands:
                logger.info("No commands to sync")
                return 0
            
            # Get guild ID if needed
            guild_id = None
            if enable_guild_sync:
                guild_id = os.getenv('DISCORD_SERVER')
                if guild_id:
                    guild_id = int(guild_id)
                    logger.info(f"Using guild ID: {guild_id} for guild sync")
            
            try:
                # First sync to the specific guild if enabled (we'll wait for this to complete)
                if enable_guild_sync and guild_id:
                    logger.info(f"Syncing commands to guild {guild_id}")
                    await asyncio.wait_for(
                        self.bot.sync_application_commands(guild_id=guild_id),
                        timeout=30
                    )
                    logger.info(f"Commands synced to guild successfully")
                elif not enable_guild_sync:
                    logger.info("Guild sync is disabled - skipping")
                
                # Then trigger global sync in the background if enabled (without waiting)
                if enable_global_sync:
                    logger.info("Starting global command sync in the background (this may take up to an hour)...")
                    
                    # Create a background task for global sync
                    asyncio.create_task(self._global_sync_background_task())
                    
                    logger.info("Global sync started in background - continuing with bot startup")
                else:
                    logger.info("Global sync is disabled - skipping")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout during guild command sync")
            except Exception as e:
                logger.error(f"Error during command sync: {e}")
            
            # Calculate and log the time taken
            sync_time = time.time() - start_time
            logger.info(f"Command sync process completed in {sync_time:.2f} seconds")
            
            return sync_time
        except Exception as e:
            sync_time = time.time() - start_time
            logger.error(f"Command sync failed after {sync_time:.2f} seconds: {e}")
            logger.exception("Detailed sync error:")
            logger.info("Proceeding with bot startup despite sync error")
            return None

    async def _global_sync_background_task(self):
        """Background task to handle global command synchronization"""
        try:
            logger.info("Global sync background task started")
            start_time = time.time()
            
            # Sync commands globally
            await self.bot.sync_application_commands()
            
            sync_time = time.time() - start_time
            logger.info(f"Global command sync completed successfully in {sync_time:.2f} seconds")
        except Exception as e:
            sync_time = time.time() - start_time
            logger.error(f"Global command sync failed after {sync_time:.2f} seconds: {e}")
            logger.info("This won't affect commands in your server, but DM commands may not work immediately")
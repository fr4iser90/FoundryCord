from app.bot.infrastructure.discord.command_sync_service import CommandSyncService
import asyncio
import os
from app.bot.infrastructure.managers.dashboard_manager import DashboardManager
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.channel_workflow import ChannelWorkflow
from app.bot.core.workflows.service_workflow import ServiceWorkflow
from app.bot.core.workflows.dashboard_workflow import DashboardWorkflow
from app.bot.core.workflows.task_workflow import TaskWorkflow
from app.bot.core.workflows.slash_commands_workflow import SlashCommandsWorkflow
from app.shared.logging import logger


class BotLifecycleManager:
    def __init__(self, bot):
        self.bot = bot
        self.services = []
        self.tasks = []
        self.commands = []
        self.ready_event = asyncio.Event()
        self.command_sync_service = None
        self.pending_commands = []  # Track commands during registration
        self.channel_setup = None
        #self.dashboard_manager = DashboardManager(bot)
        
    async def _initialize_service(self, service):
        """Initialize a service"""
        try:
            logger.info(f"Initializing service: {service['name']}")
            service_instance = await service['setup'](self.bot)
            # Speichere den Service im Bot für späteren Zugriff
            setattr(self.bot, f"{service['name'].lower().replace(' ', '_')}_service", service_instance)
            logger.info(f"Service initialized: {service['name']}")
        except Exception as e:
            logger.error(f"Failed to initialize service {service['name']}: {e}")
            raise

    async def _start_task(self, task):
        """Start a background task"""
        try:
            logger.info(f"Starting task: {task['name']}")
            asyncio.create_task(task['func'](self.bot, *task['args']))
            logger.info(f"Task started: {task['name']}")
        except Exception as e:
            logger.error(f"Failed to start task {task['name']}: {e}")
            raise

    async def add_service(self, service):
        """Add and initialize a service"""
        self.services.append(service)
        await self._initialize_service(service)
        
    async def add_task(self, task):
        """Add and start a task"""
        self.tasks.append(task)
        await self._start_task(task)

    async def add_command(self, command):
        """Add and register a command"""
        try:
            logger.info(f"Registering command: {command['name']}")
            self.bot.add_cog(command['cog'])
            self.commands.append(command)
            self.pending_commands.extend(command['cog'].application_commands)
            logger.info(f"Command registered: {command['name']}")
        except Exception as e:
            logger.error(f"Failed to register command {command['name']}: {e}")
            raise

    async def register_command(self, cog):
        """Track commands during registration (compatibility with old code)"""
        self.pending_commands.extend(cog.application_commands)
        self.bot.add_cog(cog)

    async def wait_until_ready(self, timeout=30):
        """Wait for all components to be ready"""
        try:
            await asyncio.wait_for(self.ready_event.wait(), timeout=timeout)
            logger.info("All components are ready")
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for components")

    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Starting shutdown sequence")
        
        # Shutdown tasks
        for task in self.tasks:
            try:
                logger.debug(f"Stopping task: {task['name']}")
                # Add task cleanup logic here
            except Exception as e:
                logger.error(f"Error stopping task {task['name']}: {e}")

        # Shutdown services
        for service in reversed(self.services):
            try:
                logger.debug(f"Stopping service: {service['name']}")
                # Add service cleanup logic here
            except Exception as e:
                logger.error(f"Error stopping service {service['name']}: {e}")

    async def setup_command_sync(self, enable_guild_sync=True, enable_global_sync=True, timeout=60):
        """Set up the command synchronization service"""
        try:
            logger.info("Setting up command sync service")
            self.command_sync_service = CommandSyncService(
                self.bot, 
                enable_guild_sync=enable_guild_sync,
                enable_global_sync=enable_global_sync
            )
            await self.command_sync_service.initialize()
            logger.info("Command sync service initialized")
            return self.command_sync_service
        except Exception as e:
            logger.error(f"Failed to set up command sync service: {e}")
            raise
    
    async def sync_commands(self, timeout=60):
        """Synchronize commands with Discord"""
        if not self.command_sync_service:
            logger.warning("Command sync service not initialized, setting up now")
            await self.setup_command_sync()
            
        try:
            logger.info("Starting command synchronization")
            sync_time = await self.command_sync_service.sync_all()
            logger.info(f"Command synchronization completed in {sync_time:.2f} seconds")
            return sync_time
        except Exception as e:
            logger.error(f"Command synchronization failed: {e}")
            return None
            
    async def verify_commands(self):
        """Verify commands are properly registered"""
        if not self.command_sync_service:
            logger.warning("Command sync service not initialized, setting up now")
            await self.setup_command_sync()
            
        try:
            registered = await self.command_sync_service.verify_commands()
            return len(registered) > 0
        except Exception as e:
            logger.error(f"Command verification failed: {e}")
            return False

    async def sync_commands_background(self, initial_delay=10):
        """Start command synchronization in background with a delay"""
        if not self.command_sync_service:
            logger.warning("Command sync service not initialized, setting up now")
            await self.setup_command_sync()
            
        try:
            logger.info(f"Starting background command synchronization (first sync in {initial_delay}s)")
            await self.command_sync_service.start_background_sync(initial_delay=initial_delay)
            return True
        except Exception as e:
            logger.error(f"Background command synchronization failed: {e}")
            return False

    async def initialize(self, critical_services=None, module_services=None, tasks=None):
        """Initialize all components through workflows"""
        try:
            logger.info("Starting initialization sequence")
            
            # Wait for bot ready
            if not self.bot.is_ready():
                await self.bot.wait_until_ready()
            
            # First, ensure dashboard manager exists
            if not hasattr(self.bot, 'dashboard_manager'):
                logger.info("Creating dashboard manager")
                self.bot.dashboard_manager = await DashboardManager.setup(self.bot)

            # Initialize through workflows
            workflows = [
                ('category', CategoryWorkflow(self.bot)),
                ('channel', ChannelWorkflow(self.bot)),
                ('service', ServiceWorkflow(self.bot)),
                ('dashboard', DashboardWorkflow(self.bot)),
                ('slash_commands', SlashCommandsWorkflow(self.bot)),
                ('task', TaskWorkflow(self.bot))
            ]
            
            for name, workflow in workflows:
                try:
                    logger.info(f"Initializing {name} workflow")
                    await workflow.initialize()
                except Exception as e:
                    logger.error(f"{name} workflow initialization failed: {e}")
                    raise
                
            logger.info("Initialization sequence completed")
            self.ready_event.set()
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
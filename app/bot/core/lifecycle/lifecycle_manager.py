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
from app.shared.interface.logging.api import get_bot_logger
import traceback
from typing import Dict, Any, List, Optional

logger = get_bot_logger()


class LifecycleManager:
    """Manages the bot lifecycle including initialization and shutdown sequences."""
    
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False
        self.workflows = {}
        self.services = {}
        
    async def initialize(self):
        """Initialize bot components."""
        try:
            logger.info("Starting bot initialization...")
            
            # Initialize database connection
            await self._initialize_database()
            
            # Initialize services
            await self._initialize_services()
            
            # Initialize workflows
            await self._initialize_workflows()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.initialized = True
            logger.info("Initialization sequence completed")
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
            
    async def shutdown(self):
        """Shutdown bot components gracefully."""
        try:
            logger.info("Starting bot shutdown sequence...")
            
            # Stop workflows in reverse order
            await self._shutdown_workflows()
            
            # Stop services in reverse order
            await self._shutdown_services()
            
            # Cancel all background tasks
            await self._cancel_background_tasks()
            
            logger.info("Shutdown sequence completed")
            return True
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return False
    
    async def _initialize_database(self):
        """Initialize database connections."""
        logger.info("Initializing database connections...")
        
        # Import here to avoid circular imports
        from app.shared.infrastructure.database.core.connection import ensure_db_initialized
        
        # Ensure database is initialized
        await ensure_db_initialized()
        
    async def _initialize_services(self):
        """Initialize bot services."""
        logger.info("Initializing services...")
        
        # Import service factory
        from app.bot.infrastructure.factories.composite.service_factory import ServiceFactory
        
        # Create service factory
        service_factory = ServiceFactory(self.bot)
        
        # Create core services
        self.services['config'] = await service_factory.create_config_service()
        self.services['event'] = await service_factory.create_event_service()
        
        # Register services with bot
        for name, service in self.services.items():
            self.bot.register_service(name, service)
            
    async def _initialize_workflows(self):
        """Initialize bot workflows."""
        logger.info("Initializing workflows...")
        
        # Import workflow factory
        from app.bot.infrastructure.factories.composite.workflow_factory import WorkflowFactory
        
        # Create workflow factory
        workflow_factory = WorkflowFactory(self.bot)
        
        # Initialize standard workflows
        self.workflows['channel'] = await workflow_factory.create_channel_workflow()
        self.workflows['dashboard'] = await workflow_factory.create_dashboard_workflow()
        self.workflows['slash_commands'] = await workflow_factory.create_command_workflow()
        self.workflows['task'] = await workflow_factory.create_task_workflow()
        
        # Register workflows with bot
        for name, workflow in self.workflows.items():
            self.bot.register_workflow(name, workflow)
    
    async def _start_background_tasks(self):
        """Start background tasks."""
        logger.info("Starting background tasks...")
        
        # Start any required background tasks
        for name, workflow in self.workflows.items():
            if hasattr(workflow, 'start_background_tasks'):
                await workflow.start_background_tasks()
    
    async def _shutdown_workflows(self):
        """Shutdown workflows in reverse order."""
        logger.info("Shutting down workflows...")
        
        # Get workflow names in reverse order
        workflow_names = list(self.workflows.keys())
        workflow_names.reverse()
        
        # Shutdown each workflow
        for name in workflow_names:
            workflow = self.workflows.get(name)
            if workflow:
                logger.info(f"Shutting down {name} workflow...")
                try:
                    await workflow.cleanup()
                except Exception as e:
                    logger.error(f"Error shutting down {name} workflow: {e}")
    
    async def _shutdown_services(self):
        """Shutdown services in reverse order."""
        logger.info("Shutting down services...")
        
        # Get service names in reverse order
        service_names = list(self.services.keys())
        service_names.reverse()
        
        # Shutdown each service
        for name in service_names:
            service = self.services.get(name)
            if service and hasattr(service, 'cleanup'):
                logger.info(f"Shutting down {name} service...")
                try:
                    await service.cleanup()
                except Exception as e:
                    logger.error(f"Error shutting down {name} service: {e}")
    
    async def _cancel_background_tasks(self):
        """Cancel all background tasks."""
        logger.info("Cancelling background tasks...")
        
        # Get all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        
        # Cancel all tasks
        for task in tasks:
            if not task.done():
                task.cancel()
                
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

class BotLifecycleManager:
    def __init__(self, bot):
        self.bot = bot
        self.services = {}
        self.tasks = []
        self.commands = []
        self.ready_event = asyncio.Event()
        self.command_sync_service = None
        self.pending_commands = []  # Track commands during registration
        self.channel_setup = None
        #self.dashboard_manager = DashboardManager(bot)
        
    async def _initialize_service(self, service_config):
        """Initialize a service from configuration."""
        if not service_config:
            logger.error("Cannot initialize service: service configuration is None")
            return None
            
        try:
            service_name = service_config.get('name', 'Unknown')
            service_type = service_config.get('type', service_name)
            
            logger.info(f"Initializing service: {service_name}")
            
            # Create or get service instance
            service = self.bot.service_factory.create_or_get(service_type)
            
            if not service:
                logger.error(f"Failed to create service: {service_name}")
                return None
                
            # Initialize service if needed
            if hasattr(service, 'initialize') and callable(service.initialize):
                if asyncio.iscoroutinefunction(service.initialize):
                    await service.initialize()
                else:
                    service.initialize()
                    
            # Register service locally
            self.services[service_name] = service
            
            logger.info(f"Service initialized: {service_name}")
            return service
            
        except Exception as e:
            service_name = service_config.get('name', 'Unknown') if service_config else 'Unknown'
            logger.error(f"Failed to initialize service {service_name}: {e}")
            logger.debug(traceback.format_exc())
            return None

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
                    logger.debug(traceback.format_exc())
                    raise
                
            logger.info("Initialization sequence completed")
            self.ready_event.set()
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            logger.debug(traceback.format_exc())
            raise

    def get_service(self, service_name: str):
        """Get a service by name."""
        return self.services.get(service_name)
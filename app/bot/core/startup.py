from core.services.logging.logging_commands import logger
import asyncio

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
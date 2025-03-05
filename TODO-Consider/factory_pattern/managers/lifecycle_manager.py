class BotLifecycleManager:
    def __init__(self, bot):
        self.bot = bot
        self.services = []
        self.tasks = []
        self.commands = []
        self.ready_event = asyncio.Event()
        
    async def _initialize_service(self, service):
        """Initialize a service"""
        try:
            logger.info(f"Initializing service: {service['name']}")
            await service['setup'](self.bot)
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
            logger.info(f"Command registered: {command['name']}")
        except Exception as e:
            logger.error(f"Failed to register command {command['name']}: {e}")
            raise

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
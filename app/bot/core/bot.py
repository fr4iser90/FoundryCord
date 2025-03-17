"""Core bot class with lifecycle management."""
import os
import asyncio
import nextcord
from nextcord.ext import commands

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class HomelabBot(commands.Bot):
    """Core bot class with lifecycle management."""
    
    def __init__(self, command_prefix='!', **options):
        # Set up intents if not provided in options
        if 'intents' not in options:
            options['intents'] = nextcord.Intents.all()
            
        super().__init__(command_prefix=command_prefix, **options)
        
        # Bot state
        self.ready = False
        self.lifecycle = None
        self.factory = None
        
        # Component registries
        self.services = {}
        self.workflows = {}
        
        # Set up on_ready event handler
        self.event(self.on_ready)
        
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user.name} ({self.user.id})")
        
        for guild in self.guilds:
            logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
            
        # Only initialize once
        if not self.ready:
            self.ready = True
            
            # Start initialization sequence
            try:
                from app.bot.core.main import initialize_bot
                await initialize_bot()
            except Exception as e:
                logger.error(f"Initialization error: {e}")
                
    def register_service(self, name, service):
        """Register a service with the bot."""
        self.services[name] = service
        logger.debug(f"Registered service: {name}")
        
    def register_workflow(self, name, workflow):
        """Register a workflow with the bot."""
        self.workflows[name] = workflow
        logger.debug(f"Registered workflow: {name}")
        
    def get_service(self, name):
        """Get a service by name."""
        return self.services.get(name)
        
    def get_workflow(self, name):
        """Get a workflow by name."""
        return self.workflows.get(name)
    
    async def initialize_services(self):
        """Initialize bot services."""
        # This is handled by lifecycle manager
        pass
        
    async def on_ready(self):
        """Event handler for when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        for guild in self.guilds:
            logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
            
        # Only initialize once
        if not self.ready:
            self.ready = True
            
            # Start initialization sequence
            try:
                from app.bot.core.main import initialize_bot
                await initialize_bot()
            except Exception as e:
                logger.error(f"Initialization error: {e}") 
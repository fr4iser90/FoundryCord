import nextcord
from nextcord.ext import commands
import logging

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory
from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed
from app.bot.interfaces.dashboards.components.common.embeds.error_embed import ErrorEmbed
from app.bot.application.services.dashboard.component_loader_service import ComponentLoaderService
from app.bot.infrastructure.factories.service_factory import ServiceFactory

class FoundryCord(commands.Bot):
    """Main HomeLab Discord Bot class"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize component registry and factory right in the constructor
        logger.info("Initializing component registry and factory in constructor")
        self.component_registry = ComponentRegistry()
        self.component_factory = ComponentFactory(self.component_registry)
        # Initialize service_factory attribute to None initially
        self.service_factory = None 
        self._default_components_registered = False
        
    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        await super().setup_hook()
        
        logger.info("Starting bot initialization...")
        
        # --- ADD SERVICE FACTORY INITIALIZATION HERE ---
        logger.info("Initializing Service Factory...")
        try:
            self.service_factory = ServiceFactory(self)
            # --- ADD DEBUG LOG ---
            factory_type = type(self.service_factory).__name__ if self.service_factory else 'None'
            logger.info(f"[DEBUG bot.py] Service Factory assigned in setup_hook. Bot ID: {self.user.id}, Factory Type: {factory_type}")
            # ---------------------
        except Exception as e:
             logger.critical(f"CRITICAL: Failed to initialize Service Factory: {e}", exc_info=True)
             # Depending on severity, you might want to prevent the bot from fully starting
             # For now, we log critically and continue, but dependent services might fail.
        # ---------------------------------------------
        
        # Make sure we register components if not done in constructor
        if not self._default_components_registered:
            self.register_default_components()
        
        # ... continue with other setup ...
        
        await self.setup_dashboards()
        
        # Check if service_factory exists before using it to register ComponentLoaderService
        if self.service_factory:
            self.component_loader = ComponentLoaderService(self)
            # Ensure service_factory has the registration method before calling
            if hasattr(self.service_factory, 'register_service') and hasattr(self.service_factory, 'has_service'):
                if not self.service_factory.has_service('component_loader'):
                    self.service_factory.register_service(
                        'component_loader', 
                        self.component_loader
                    )
            else:
                 logger.error("Service Factory instance does not have expected registration methods.")
        else:
            logger.error("Service Factory not available when trying to register ComponentLoaderService.")
    
    def register_default_components(self):
        """Register the default UI components"""
        try:
            # CORE EMBED COMPONENTS
            # Register standard dashboard embed
            self.component_registry.register_component(
                component_type="dashboard_embed",
                component_class=DashboardEmbed,
                description="Standard dashboard embed",
                default_config={
                    "title": "Dashboard",
                    "color": nextcord.Color.blurple().value,
                    "timestamp": True
                }
            )
            
            # Register error embed component
            self.component_registry.register_component(
                component_type="error_embed",
                component_class=ErrorEmbed,
                description="Embed for displaying errors",
                default_config={
                    "title": "Error",
                    "description": "An error occurred",
                    "color": nextcord.Color.red().value,
                    "error_code": None
                }
            )
            
            # You could add more component registrations here in a data-driven way
            # For example, you could load component registrations from a config file
            # or database rather than hardcoding them
            
            self._default_components_registered = True
            logger.info(f"Registered {len(self.component_registry.get_all_component_types())} default components")
        except Exception as e:
            logger.error(f"Error registering default components: {str(e)}")

    async def setup_dashboards(self):
        """Set up dashboard system."""
        try:
            # Load dashboard registry
            from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry
            self.dashboard_registry = DashboardRegistry(self)
            await self.dashboard_registry.initialize()
            
            # Load dashboard commands
            await self.load_extension("app.bot.commands.dashboard.dashboard_command")
            
            logger.info("Dashboard system initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up dashboard system: {e}")
            return False 
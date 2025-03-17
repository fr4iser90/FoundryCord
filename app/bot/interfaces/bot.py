import discord
from discord.ext import commands
import logging

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory
from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed

class HomelabBot(commands.Bot):
    """Main HomeLab Discord Bot class"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize component registry and factory right in the constructor
        logger.info("Initializing component registry and factory in constructor")
        self.component_registry = ComponentRegistry()
        self.component_factory = ComponentFactory(self.component_registry)
        self._default_components_registered = False
        
    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        await super().setup_hook()
        
        logger.info("Starting bot initialization...")
        
        # Make sure we register components if not done in constructor
        if not self._default_components_registered:
            self.register_default_components()
        
        # ... continue with other setup ...
    
    def register_default_components(self):
        """Register the default UI components"""
        try:
            # Register basic components
            self.component_registry.register_component(
                component_type="dashboard_embed",
                component_class=DashboardEmbed,
                description="Standard dashboard embed",
                default_config={
                    "title": "Dashboard",
                    "color": discord.Color.blurple().value,
                    "timestamp": True
                }
            )
            
            # Register more components as they're implemented
            # self.component_registry.register_component(...)
            
            self._default_components_registered = True
            logger.info(f"Registered {len(self.component_registry.get_all_component_types())} default components")
        except Exception as e:
            logger.error(f"Error registering default components: {str(e)}") 
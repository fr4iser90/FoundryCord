from typing import List, Dict, Any, Optional
import nextcord
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Remove ALL imports that lead to circular dependencies
# from app.bot.infrastructure.factories.base.base_factory import BaseFactory
# from .base_dashboard_factory import BaseDashboardFactory

class DashboardFactory:
    """Factory for creating dashboard components"""
    
    def __init__(self, bot):
        self.bot = bot
        self._registry = {}  # Local registry without BaseFactory dependency
        
    @property
    def view_factory(self):
        return self.bot.component_factory.factories['view']
        
    @property
    def message_factory(self):
        return self.bot.component_factory.factories['message']
        
    @property
    def button_factory(self):
        return self.bot.component_factory.factories['button']
        
    @property
    def menu_factory(self):
        return self.bot.component_factory.factories['menu']
        
    @property
    def modal_factory(self):
        return self.bot.component_factory.factories['modal']
        
    def register(self, key: str, component: Any) -> None:
        """Register a component in the factory registry"""
        self._registry[key] = component
        logger.debug(f"Registered {key} in DashboardFactory")
        
    def get(self, key: str) -> Any:
        """Get a registered component"""
        return self._registry.get(key)

    async def create_dashboard(self,
        title: str,
        description: str,
        components: List[Dict[str, Any]],
        color: int = 0x3498db,
        timeout: int = 600
    ) -> tuple[nextcord.Embed, nextcord.ui.View]:
        """
        Creates a dashboard with specified components
        
        Args:
            title: Dashboard title
            description: Dashboard description
            components: List of component configs
            color: Embed color
            timeout: View timeout in seconds
        """
        # Create embed
        embed = await self.message_factory.create_embed(
            title=title,
            description=description,
            color=color
        )

        # Create view
        view = nextcord.ui.View(timeout=timeout)

        # Add components
        for comp in components:
            component = None
            
            if comp['type'] == 'button':
                component = self.button_factory.create_confirm_button(
                    custom_id=comp.get('custom_id'),
                    label=comp.get('label', 'Button')
                )
            
            elif comp['type'] == 'role_menu':
                component = self.menu_factory.create_role_select(
                    custom_id=comp.get('custom_id'),
                    placeholder=comp.get('placeholder', 'Select roles')
                )
                
            elif comp['type'] == 'user_menu':
                component = self.menu_factory.create_user_select(
                    custom_id=comp.get('custom_id'),
                    placeholder=comp.get('placeholder', 'Select users')
                )

            if component:
                view.add_item(component)

        return embed, view

    async def create(self, dashboard_type: str, **kwargs) -> Dict[str, Any]:
        """Implementation of create method without BaseFactory dependency"""
        try:
            # Ensure dashboard manager exists
            if not hasattr(self.bot, 'dashboard_manager'):
                # Lazy import to avoid circular dependency
                from app.bot.infrastructure.managers.dashboard_manager import DashboardManager
                logger.warning("Dashboard manager not initialized, creating now")
                self.bot.dashboard_manager = await DashboardManager.setup(self.bot)
            
            # Check for existing dashboard instance first
            existing = self.bot.dashboard_manager.get_dashboard(dashboard_type)
            if existing:
                logger.info(f"Reusing existing dashboard instance for {dashboard_type}")
                return {
                    'name': dashboard_type,
                    'dashboard': existing,
                    'type': 'dashboard'
                }
            
            # Lazy import the dashboard service
            try:
                logger.error("DashboardFactory.create is broken - Static constants removed.")
                # TODO: Rework service loading logic. Need a dynamic way to map dashboard_type to service class.
                return None # Return None as logic is broken

            except ImportError as e:
                logger.error(f"Failed to import dashboard service: {e}")
                return None
        except Exception as e:
            logger.error(f"Failed to create dashboard {dashboard_type}: {e}")
            return None
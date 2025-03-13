from typing import List, Dict, Any, Optional
import nextcord
from ..base.base_factory import BaseFactory
import logging
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_SERVICES
from app.shared.logging import logger

logger = logging.getLogger(__name__)

class DashboardFactory(BaseFactory):
    def __init__(self, bot):
        super().__init__(bot)
        
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
                [
                    {
                        'type': 'button'|'role_menu'|'user_menu'|'text_input',
                        'style': nextcord.ButtonStyle,
                        'label': str,
                        'custom_id': str,
                        'emoji': str,
                        'placeholder': str,
                        ...
                    }
                ]
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

    async def create_settings_dashboard(self,
        guild_name: str,
        settings: Dict[str, Any]
    ) -> tuple[nextcord.Embed, nextcord.ui.View]:
        """Predefined settings dashboard template"""
        components = [
            {
                'type': 'button',
                'label': 'General Settings',
                'custom_id': 'general_settings',
                'emoji': '⚙️'
            },
            {
                'type': 'button',
                'label': 'Permissions',
                'custom_id': 'permissions',
                'emoji': '🔒'
            },
            {
                'type': 'role_menu',
                'custom_id': 'admin_roles',
                'placeholder': 'Configure admin roles'
            }
        ]
        
        return await self.create_dashboard(
            title=f"Settings - {guild_name}",
            description="Configure your server settings here.",
            components=components
        )

    async def create_help_dashboard(self,
        commands: List[Dict[str, str]]
    ) -> tuple[nextcord.Embed, nextcord.ui.View]:
        """Predefined help dashboard template"""
        components = [
            {
                'type': 'button',
                'label': 'Commands',
                'custom_id': 'view_commands',
                'emoji': '📜'
            },
            {
                'type': 'button',
                'label': 'Support',
                'custom_id': 'get_support',
                'emoji': '❓'
            }
        ]
        
        return await self.create_dashboard(
            title="Help Center",
            description="Get help and information about the bot.",
            components=components
        )

    async def create(self, dashboard_type: str, **kwargs) -> Dict[str, Any]:
        try:
            # Ensure dashboard manager exists
            if not hasattr(self.bot, 'dashboard_manager'):
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
            
            # Create new if doesn't exist
            service_name = DASHBOARD_SERVICES.get(dashboard_type)
            if not service_name:
                logger.warning(f"Unknown dashboard type: {dashboard_type}")
                return None
            
            # Create and register new dashboard
            dashboard = service_class(self.bot, self)
            await dashboard.initialize()
            self.bot.dashboard_manager.register_dashboard(dashboard_type, dashboard)
            
            return {
                'name': dashboard_type,
                'dashboard': dashboard,
                'type': 'dashboard'
            }
        except Exception as e:
            logger.error(f"Failed to create dashboard {dashboard_type}: {e}")
            return None
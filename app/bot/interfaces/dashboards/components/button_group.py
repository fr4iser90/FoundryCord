"""Button group component for dashboards."""
from typing import Dict, Any, Optional, List, Callable
import nextcord
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from .base_component import DashboardComponent

class ButtonGroupComponent(DashboardComponent):
    """Component to display a group of buttons with actions"""
    
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]) -> None:
        """Button groups don't render to embeds directly."""
        # Optionally add a field about the buttons if title is provided
        if 'title' in config:
            embed.add_field(
                name=config['title'],
                value=config.get('description', 'Use the buttons below'),
                inline=config.get('inline', False)
            )
    
    async def create_ui_component(self, view: nextcord.ui.View, data: Any, 
                                 config: Dict[str, Any], dashboard_id: str) -> Optional[List[nextcord.ui.Button]]:
        """Create button group UI components."""
        try:
            buttons = []
            buttons_config = config.get('buttons', [])
            
            if not buttons_config:
                logger.warning(f"No buttons configured for button group {self.id}")
                return None
                
            for button_config in buttons_config:
                try:
                    # Get button properties
                    label = button_config.get('label', 'Button')
                    style_name = button_config.get('style', 'primary')
                    emoji = button_config.get('emoji')
                    action = button_config.get('action')
                    disabled = button_config.get('disabled', False)
                    url = button_config.get('url')
                    row = button_config.get('row', 0)
                    
                    # Map style name to ButtonStyle
                    style_map = {
                        'primary': nextcord.ButtonStyle.primary,
                        'secondary': nextcord.ButtonStyle.secondary,
                        'success': nextcord.ButtonStyle.success,
                        'danger': nextcord.ButtonStyle.danger,
                        'url': nextcord.ButtonStyle.url,
                        'blurple': nextcord.ButtonStyle.primary,
                        'grey': nextcord.ButtonStyle.secondary,
                        'gray': nextcord.ButtonStyle.secondary,
                        'green': nextcord.ButtonStyle.success,
                        'red': nextcord.ButtonStyle.danger
                    }
                    style = style_map.get(style_name.lower(), nextcord.ButtonStyle.primary)
                    
                    # Create button
                    if url:
                        # URL button doesn't need custom_id
                        button = nextcord.ui.Button(
                            style=nextcord.ButtonStyle.url,
                            label=label,
                            url=url,
                            emoji=emoji,
                            row=row
                        )
                    else:
                        # Create action button
                        button = DashboardButton(
                            style=style,
                            label=label,
                            custom_id=f"{dashboard_id}_{self.id}_{action}",
                            emoji=emoji,
                            disabled=disabled,
                            row=row,
                            action=action,
                            dashboard_id=dashboard_id,
                            component_id=self.id
                        )
                    
                    view.add_item(button)
                    buttons.append(button)
                    
                except Exception as e:
                    logger.error(f"Error creating button {button_config.get('label')}: {e}")
            
            return buttons
            
        except Exception as e:
            logger.error(f"Error creating button group: {e}")
            return None
    
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any,
                           config: Dict[str, Any], dashboard_id: str, action: str) -> None:
        """Handle button interactions."""
        try:
            # Defer response to avoid interaction timeout
            await interaction.response.defer(ephemeral=True)
            
            # Get handler for this action
            handlers = config.get('handlers', {})
            handler_config = handlers.get(action)
            
            if not handler_config:
                await interaction.followup.send(f"No handler configured for action: {action}", ephemeral=True)
                return
                
            # Get handler type
            handler_type = handler_config.get('type', 'function')
            
            if handler_type == 'function':
                # Call a function handler
                function_name = handler_config.get('function')
                if not function_name:
                    await interaction.followup.send("Function handler not configured properly", ephemeral=True)
                    return
                    
                # Try to get the function from the bot
                function = getattr(self.bot, function_name, None)
                if not function or not callable(function):
                    function = self._get_service_function(function_name)
                    
                if function and callable(function):
                    # Call function with parameters
                    params = handler_config.get('params', {})
                    result = await function(interaction=interaction, **params)
                    
                    # Send result if it's a string
                    if isinstance(result, str):
                        await interaction.followup.send(result, ephemeral=True)
                else:
                    await interaction.followup.send(f"Function {function_name} not found", ephemeral=True)
                    
            elif handler_type == 'message':
                # Send a message
                message = handler_config.get('message', 'Button pressed')
                await interaction.followup.send(message, ephemeral=True)
                
            elif handler_type == 'refresh':
                # Refresh the dashboard
                # Get dashboard controller
                dashboard_manager = self.bot.get_service('dashboard_manager')
                if dashboard_manager:
                    controller = await dashboard_manager.get_dashboard_controller(dashboard_id)
                    if controller:
                        await controller.refresh_data()
                        await controller.display_dashboard()
                        await interaction.followup.send("Dashboard refreshed!", ephemeral=True)
                    else:
                        await interaction.followup.send("Dashboard controller not found.", ephemeral=True)
                else:
                    await interaction.followup.send("Dashboard manager not available.", ephemeral=True)
                    
            else:
                await interaction.followup.send(f"Unknown handler type: {handler_type}", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error handling button interaction: {e}")
            await interaction.followup.send(f"Error processing button action: {str(e)}", ephemeral=True)
            
    def _get_service_function(self, function_name: str) -> Optional[Callable]:
        """Get a function from a service."""
        try:
            if '.' in function_name:
                # Format: service_name.method_name
                service_name, method_name = function_name.split('.', 1)
                
                # Get service
                service = self.bot.get_service(service_name)
                if service:
                    # Get method
                    method = getattr(service, method_name, None)
                    if method and callable(method):
                        return method
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting service function {function_name}: {e}")
            return None

class DashboardButton(nextcord.ui.Button):
    """Button with dashboard action."""
    
    def __init__(self, dashboard_id: str, component_id: str, action: str, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_id = dashboard_id
        self.component_id = component_id
        self.action = action
        
    async def callback(self, interaction: nextcord.Interaction):
        """Handle button click."""
        try:
            # Get component registry
            component_registry = interaction.client.get_service('component_registry')
            if not component_registry:
                await interaction.response.send_message(
                    "Component registry not available", 
                    ephemeral=True
                )
                return
                
            # Get component implementation
            component_impl = component_registry.get_component('button_group')
            if not component_impl:
                await interaction.response.send_message(
                    "Button group component not available", 
                    ephemeral=True
                )
                return
                
            # Get dashboard config
            dashboard_repository = interaction.client.get_service('dashboard_repository')
            if not dashboard_repository:
                await interaction.response.send_message(
                    "Dashboard repository not available", 
                    ephemeral=True
                )
                return
                
            # Get dashboard config
            config = await dashboard_repository.get_dashboard_config(self.dashboard_id)
            if not config:
                await interaction.response.send_message(
                    "Dashboard configuration not available", 
                    ephemeral=True
                )
                return
                
            # Find component config
            component_config = next(
                (c for c in config.get('components', []) if c['id'] == self.component_id), 
                None
            )
            
            if not component_config:
                await interaction.response.send_message(
                    "Component configuration not found", 
                    ephemeral=True
                )
                return
                
            # Create component and handle interaction
            component = component_impl(interaction.client, component_config)
            await component.on_interaction(
                interaction, 
                None,  # No data needed for button interaction
                component_config.get('config', {}), 
                self.dashboard_id,
                self.action
            )
            
        except Exception as e:
            logger.error(f"Error handling button callback: {e}")
            await interaction.response.send_message(
                f"Error processing button: {str(e)}", 
                ephemeral=True
            ) 
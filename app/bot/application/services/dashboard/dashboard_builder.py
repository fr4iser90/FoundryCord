"""Service for building dashboard instances."""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

#from app.shared.domain.OLD import DashboardModel
from app.bot.infrastructure.factories.component_registry import ComponentRegistry

class DashboardBuilder:
    """Service for building Discord UI elements from dashboard models."""
    
    def __init__(self, bot, component_registry: ComponentRegistry):
        self.bot = bot
        self.component_registry = component_registry
        
    async def build_dashboard(self, dashboard: DashboardModel, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a complete dashboard from a model and data."""
        try:
            # Create the embed
            embed = await self.build_embed(dashboard, data)
            
            # Create the view
            view = await self.build_view(dashboard, data)
            
            return {
                'embed': embed,
                'view': view,
                'dashboard': dashboard
            }
        except Exception as e:
            logger.error(f"Error building dashboard {dashboard.id}: {e}")
            raise
            
    async def build_embed(self, dashboard: DashboardModel, data: Dict[str, Any]) -> nextcord.Embed:
        """Build a Discord embed from dashboard configuration."""
        try:
            # Create base embed
            embed_config = dashboard.embed
            embed = nextcord.Embed(
                title=embed_config.get('title', dashboard.title),
                description=embed_config.get('description', dashboard.description),
                color=int(embed_config.get('color', '0x3498db'), 16)
            )
            
            # Add timestamp
            embed.timestamp = datetime.now()
            
            # Process each component to add fields to the embed
            for component_config in dashboard.components:
                # Skip components that don't go in the embed (e.g., buttons)
                if component_config.id in dashboard.interactive_components:
                    continue
                    
                # Get the component implementation
                component_impl = self.component_registry.get_component(component_config.type.value)
                if not component_impl:
                    logger.warning(f"Component type not found: {component_config.type}")
                    continue
                    
                # Get data for this component
                component_data = None
                if component_config.data_source_id:
                    component_data = data.get(component_config.data_source_id)
                    
                # Render the component to the embed
                await component_impl.render_to_embed(embed, component_data, component_config.config)
                
            # Add footer
            if 'footer' in embed_config:
                embed.set_footer(
                    text=embed_config['footer'].get('text', f"Dashboard: {dashboard.id}"),
                    icon_url=embed_config['footer'].get('icon_url')
                )
                
            return embed
        except Exception as e:
            logger.error(f"Error building embed for dashboard {dashboard.id}: {e}")
            raise
            
    async def build_view(self, dashboard: DashboardModel, data: Dict[str, Any]) -> nextcord.ui.View:
        """Build a Discord view with interactive components."""
        try:
            view = nextcord.ui.View(timeout=None)
            
            # Process interactive components
            for component_id in dashboard.interactive_components:
                # Find component config
                component_config = next((c for c in dashboard.components if c.id == component_id), None)
                if not component_config:
                    logger.warning(f"Interactive component not found: {component_id}")
                    continue
                    
                # Get component implementation
                component_impl = self.component_registry.get_component(component_config.type.value)
                if not component_impl:
                    logger.warning(f"Component type not found: {component_config.type}")
                    continue
                    
                # Get data for this component
                component_data = None
                if component_config.data_source_id:
                    component_data = data.get(component_config.data_source_id)
                    
                # Create UI component
                ui_component = await component_impl.create_ui_component(
                    view, component_data, component_config.config, dashboard.id
                )
                
                # Add to view if not None
                if ui_component and hasattr(view, 'add_item'):
                    view.add_item(ui_component)
                    
            return view
        except Exception as e:
            logger.error(f"Error building view for dashboard {dashboard.id}: {e}")
            raise 
"""Service for building dashboard instances."""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity
from app.bot.infrastructure.factories.component_registry import ComponentRegistry

class DashboardBuilder:
    """Service for building Discord UI elements from dashboard models."""
    
    def __init__(self, bot, component_registry: ComponentRegistry):
        self.bot = bot
        self.component_registry = component_registry
        
    async def build_dashboard(self, dashboard: DashboardEntity, data: Dict[str, Any]) -> Dict[str, Any]:
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
            
    async def build_embed(self, dashboard: DashboardEntity, data: Dict[str, Any]) -> nextcord.Embed:
        """Build a Discord embed from dashboard configuration."""
        try:
            # Create base embed
            embed_config = dashboard.config.get('embed', {})
            embed = nextcord.Embed(
                title=embed_config.get('title', dashboard.name),
                description=embed_config.get('description', dashboard.description),
                color=int(embed_config.get('color', '0x3498db'), 16)
            )
            
            # Add timestamp
            embed.timestamp = datetime.now()
            
            # Process each component to add fields to the embed
            for component in dashboard.components:
                # Skip components that don't go in the embed (e.g., buttons)
                if component.component_type in ['button', 'selector']:
                    continue
                    
                # Get the component implementation
                component_impl = self.component_registry.get_component(component.component_type)
                if not component_impl:
                    logger.warning(f"Component type not found: {component.component_type}")
                    continue
                    
                # Get data for this component
                component_data = None
                if component.config and 'data_source_id' in component.config:
                    component_data = data.get(component.config['data_source_id'])
                    
                # Render the component to the embed
                await component_impl.render_to_embed(embed, component_data, component.config)
                
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
            
    async def build_view(self, dashboard: DashboardEntity, data: Dict[str, Any]) -> nextcord.ui.View:
        """Build a Discord view with interactive components."""
        try:
            view = nextcord.ui.View(timeout=None)
            
            # Process interactive components
            for component in dashboard.components:
                if component.component_type not in ['button', 'selector']:
                    continue
                    
                # Get component implementation
                component_impl = self.component_registry.get_component(component.component_type)
                if not component_impl:
                    logger.warning(f"Component type not found: {component.component_type}")
                    continue
                    
                # Get data for this component
                component_data = None
                if component.config and 'data_source_id' in component.config:
                    component_data = data.get(component.config['data_source_id'])
                    
                # Create UI component
                ui_component = await component_impl.create_ui_component(
                    view, component_data, component.config, dashboard.id
                )
                
                # Add to view if not None
                if ui_component and hasattr(view, 'add_item'):
                    view.add_item(ui_component)
                    
            return view
        except Exception as e:
            logger.error(f"Error building view for dashboard {dashboard.id}: {e}")
            raise 
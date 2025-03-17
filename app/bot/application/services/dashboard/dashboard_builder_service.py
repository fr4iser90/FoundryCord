"""Service for building dashboard instances."""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardBuilderService:
    """Service for building Discord UI elements from dashboard configurations."""
    
    def __init__(self, bot):
        self.bot = bot
        self.component_registry = None
        self.data_source_registry = None
        
    async def initialize(self):
        """Initialize the dashboard builder."""
        try:
            # Get registry services
            self.component_registry = self.bot.get_service('component_registry')
            self.data_source_registry = self.bot.get_service('data_source_registry')
            
            if not self.component_registry:
                logger.error("Component Registry service not available")
                return False
                
            if not self.data_source_registry:
                logger.warning("Data Source Registry service not available")
                # We'll continue without it
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Dashboard Builder Service: {e}")
            return False
            
    async def build_dashboard(self, config: Dict[str, Any], data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a dashboard from configuration and data."""
        try:
            # Default empty data
            if data is None:
                data = {}
                
            # Fetch data if needed and not provided
            if not data and 'data_sources' in config:
                data = await self.fetch_data(config.get('data_sources', {}))
                
            # Create the embed
            embed = await self.build_embed(config, data)
            
            # Create the view
            view = await self.build_view(config, data)
            
            return {
                'embed': embed,
                'view': view,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Error building dashboard: {e}")
            
            # Return a minimal error dashboard
            embed = nextcord.Embed(
                title="Dashboard Error",
                description=f"Error building dashboard: {str(e)}",
                color=0xFF0000
            )
            
            return {
                'embed': embed,
                'view': None,
                'data': {}
            }
            
    async def build_embed(self, config: Dict[str, Any], data: Dict[str, Any]) -> nextcord.Embed:
        """Build an embed from configuration and data."""
        try:
            # Basic embed properties
            title = config.get('title', 'Dashboard')
            description = config.get('description', '')
            color = config.get('color', 0x3498db)
            
            if isinstance(color, str) and color.startswith('0x'):
                color = int(color, 16)
                
            embed = nextcord.Embed(
                title=title,
                description=description,
                color=color
            )
            
            # Add timestamp
            embed.timestamp = datetime.now()
            
            # Add footer
            footer_config = config.get('footer', {})
            if footer_config:
                embed.set_footer(
                    text=footer_config.get('text', 'HomeLab Discord Bot'),
                    icon_url=footer_config.get('icon_url')
                )
                
            # Add author
            author_config = config.get('author', {})
            if author_config:
                embed.set_author(
                    name=author_config.get('name'),
                    url=author_config.get('url'),
                    icon_url=author_config.get('icon_url')
                )
                
            # Add components
            component_configs = config.get('components', [])
            for component_config in component_configs:
                await self.add_component_to_embed(embed, component_config, data)
                
            return embed
            
        except Exception as e:
            logger.error(f"Error building embed: {e}")
            
            # Return a minimal error embed
            return nextcord.Embed(
                title="Embed Error",
                description=f"Error building embed: {str(e)}",
                color=0xFF0000
            )
            
    async def add_component_to_embed(self, embed: nextcord.Embed, component_config: Dict[str, Any], data: Dict[str, Any]):
        """Add a component to an embed."""
        if not self.component_registry:
            logger.error("Component Registry not available")
            return
            
        component_type = component_config.get('type')
        component_impl = self.component_registry.get_component(component_type)
        
        if not component_impl:
            logger.error(f"Component type not found: {component_type}")
            return
            
        # Create component and render to embed
        component = component_impl(self.bot, component_config)
        await component.render_to_embed(embed, data, component_config.get('config', {}))
            
    async def build_view(self, config: Dict[str, Any], data: Dict[str, Any]) -> Optional[nextcord.ui.View]:
        """Build a view from configuration and data."""
        try:
            # Check if there are interactive components
            interactive_components = config.get('interactive_components', [])
            
            if not interactive_components:
                return None
                
            # Create view
            view = nextcord.ui.View(timeout=None)
            
            # Add components to view
            component_configs = config.get('components', [])
            for component_id in interactive_components:
                # Find component config
                component_config = None
                for config_item in component_configs:
                    if config_item.get('id') == component_id:
                        component_config = config_item
                        break
                        
                if not component_config:
                    logger.warning(f"Interactive component not found: {component_id}")
                    continue
                    
                # Create and add component to view
                await self.add_component_to_view(view, component_config, data, config.get('id', 'unknown'))
                
            return view
            
        except Exception as e:
            logger.error(f"Error building view: {e}")
            return None
            
    async def add_component_to_view(self, view: nextcord.ui.View, component_config: Dict[str, Any], 
                                  data: Dict[str, Any], dashboard_id: str):
        """Add a component to a view."""
        if not self.component_registry:
            logger.error("Component Registry not available")
            return
            
        component_type = component_config.get('type')
        component_impl = self.component_registry.get_component(component_type)
        
        if not component_impl:
            logger.error(f"Component type not found: {component_type}")
            return
            
        # Create component and add to view
        component = component_impl(self.bot, component_config)
        component.dashboard_id = dashboard_id
        await component.add_to_view(view, data, component_config.get('config', {}))
            
    async def fetch_data(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from all data sources."""
        data = {}
        
        if not self.data_source_registry:
            # Try to use system metrics service directly
            system_metrics = self.bot.get_service('system_metrics')
            if system_metrics:
                data['system_metrics'] = await system_metrics.get_metrics()
            return data
        
        for source_id, source_config in data_sources.items():
            try:
                source_type = source_config.get('type')
                data_source = self.data_source_registry.create_data_source(source_type, source_config)
                
                if not data_source:
                    logger.warning(f"Could not create data source: {source_type}")
                    continue
                    
                # Fetch data
                result = await data_source.fetch_data(source_config.get('params', {}))
                data[source_id] = result
                
            except Exception as e:
                logger.error(f"Error fetching data from source {source_id}: {e}")
                data[source_id] = {"error": str(e)}
                
        return data 
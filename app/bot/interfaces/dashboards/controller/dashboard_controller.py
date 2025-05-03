import nextcord
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from .base_dashboard import BaseDashboardController
# Assuming DashboardDataService will be accessible, e.g., via service factory
# from app.bot.application.services.dashboard.dashboard_data_service import DashboardDataService

# TODO: Need access to ComponentRegistry, potentially passed during initialization or via bot
# from app.bot.core.registries.component_registry import ComponentRegistry 

class DashboardController(BaseDashboardController):
    """
    Dashboard controller that handles all dashboard types
    through configuration rather than inheritance
    """
    
    def __init__(self, dashboard_id: str, channel_id: int, dashboard_type: str, **kwargs):
        """Initialize the dashboard controller from configuration"""
        # Dashboard identification
        self.dashboard_id = dashboard_id
        self.channel_id = channel_id
        self.guild_id = kwargs.get('guild_id')
        self.dashboard_type = dashboard_type
        
        # Configuration
        self.config = kwargs.get('config', {})
        self.title = kwargs.get('title', "Dashboard")
        self.description = kwargs.get('description', "")
        
        # Component definitions
        self.registered_embeds = {}
        self.registered_views = {}
        self.registered_buttons = {}
        self.registered_handlers = {}
        
        # State tracking
        self.bot = None
        self.message_id = kwargs.get('message_id', None)
        self.message = None
        self.components = {}
        self.initialized = False
        self.rate_limits = {}
        
        # Dependencies (to be initialized)
        self.component_registry = None 
        self.data_service = None # Renamed from builder service
        
        logger.info(f"Initialized universal dashboard controller for {dashboard_type} dashboard {dashboard_id}")
    
    async def initialize(self, bot):
        """Initialize the dashboard controller"""
        self.bot = bot
        
        # Get Component Registry & Data Service
        try:
            # TODO: Determine the correct way to get registry/service instances
            # Using service factory as the likely approach
            if hasattr(bot, 'service_factory'):
                 self.component_registry = bot.service_factory.get_service('component_registry')
                 self.data_service = bot.service_factory.get_service('dashboard_data_service') # Use new name
            else:
                 logger.error("Service factory not available on bot instance.")
                 # Decide handling
                 return False
            
            if not self.component_registry:
                logger.error("Component Registry not available for DashboardController")
                # Decide handling
                # return False 
            if not self.data_service:
                 logger.error("DashboardDataService not available for DashboardController")
                 # Decide handling
                 # return False
                
        except Exception as e:
            logger.error(f"Error getting services/registries: {e}")
            return False
            
        # Load dashboard definition from database
        await self.load_dashboard_definition() # This loads self.config, self.title etc.
        
        # Register standard handlers
        self.register_standard_handlers()
        
        self.initialized = True
        logger.info(f"Dashboard {self.dashboard_id} initialization complete")
        return True
    
    async def load_dashboard_definition(self):
        """
        Load dashboard definition from database
        This is the key method that makes the controller flexible
        """
        logger.info(f"Loading definition for {self.dashboard_type} dashboard {self.dashboard_id}")
        
        try:
            # Get dashboard repository from service factory
            dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
            if not dashboard_repo:
                raise ValueError("Dashboard repository service not available")
            
            # Load dashboard configuration from database
            dashboard = await dashboard_repo.get_dashboard_by_id(self.dashboard_id)
            if not dashboard:
                # Try to find by channel ID + type
                dashboard = await dashboard_repo.get_dashboard_by_channel_and_type(
                    self.channel_id, self.dashboard_type
                )
            
            if not dashboard:
                logger.warning(f"No dashboard found for ID {self.dashboard_id}, creating default")
                # Create a default dashboard if not found
                await self.create_default_dashboard()
                return
            
            # Load components from the database
            await self.load_components_from_database(dashboard)
            
            # Update properties from database
            self.title = dashboard.title or self.title
            self.description = dashboard.description or self.description
            self.config = dashboard.config or self.config
            self.message_id = dashboard.message_id or self.message_id
            
            logger.info(f"Loaded dashboard definition for {self.dashboard_id} from database")
            
        except Exception as e:
            logger.error(f"Error loading dashboard definition from database: {e}")
            # Create a default dashboard if loading fails
            await self.create_default_dashboard()
    
    async def load_components_from_database(self, dashboard):
        """Load components for a dashboard from the database"""
        try:
            # Load components through the repository
            components = await self.bot.service_factory.get_service('dashboard_repository').get_components_for_dashboard(dashboard.id)
            
            for component in components:
                # Process each component based on its type
                if component.component_type == 'button':
                    self.register_button(
                        component.custom_id,
                        component.config.get('label', 'Button'),
                        component.config.get('style', 'primary'),
                        component.config.get('emoji'),
                        component.config.get('row', 0),
                        component.config.get('disabled', False)
                    )
                elif component.component_type == 'embed':
                    self.register_embed(
                        component.custom_id,
                        component.config.get('title'),
                        component.config.get('description'),
                        component.config.get('color'),
                        component.config.get('fields', []),
                        component.config.get('footer')
                    )
                # Add more component types as needed
                
            logger.info(f"Loaded {len(components)} components for dashboard {dashboard.id}")
            
        except Exception as e:
            logger.error(f"Error loading components from database: {e}")
    
    async def create_default_dashboard(self):
        """Create a default dashboard configuration"""
        logger.info(f"Creating default dashboard for {self.dashboard_type}")
        
        # Create a basic embed
        self.register_embed(
            "main_embed",
            f"{self.dashboard_type.capitalize()} Dashboard",
            "This dashboard was created with default settings",
            0x3498db,  # Blue color
            []  # No fields
        )
        
        # Create a refresh button
        self.register_button(
            "refresh_button",
            "Refresh",
            "secondary",
            "🔄",
            0,  # Row 0
            False  # Not disabled
        )
        
        # Register the refresh handler
        self.register_handler("refresh_button", self.on_refresh)
    
    def register_embed(self, embed_id, title=None, description=None, color=None, fields=None, footer=None):
        """Register an embed configuration"""
        self.registered_embeds[embed_id] = {
            'title': title,
            'description': description,
            'color': color,
            'fields': fields or [],
            'footer': footer
        }
        logger.debug(f"Registered embed {embed_id} for dashboard {self.dashboard_id}")
    
    def register_button(self, button_id, label, style="primary", emoji=None, row=0, disabled=False):
        """Register a button configuration"""
        self.registered_buttons[button_id] = {
            'label': label,
            'style': style,
            'emoji': emoji,
            'row': row,
            'disabled': disabled
        }
        logger.debug(f"Registered button {button_id} for dashboard {self.dashboard_id}")
    
    def register_handler(self, component_id, handler_func):
        """Register a handler function for a component"""
        self.registered_handlers[component_id] = handler_func
        logger.debug(f"Registered handler for {component_id} on dashboard {self.dashboard_id}")
    
    def register_standard_handlers(self):
        """Register standard handlers for common components"""
        # Register refresh button handler if it exists
        if "refresh_button" in self.registered_buttons and "refresh_button" not in self.registered_handlers:
            self.register_handler("refresh_button", self.on_refresh)
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Standard refresh button handler"""
        # Check rate limiting (inherited from BaseDashboardController)
        if not await self.check_rate_limit(interaction, "refresh", 5):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        # Refresh the dashboard
        await self.display_dashboard()
        
        await interaction.followup.send("Dashboard refreshed!", ephemeral=True)
    
    async def handle_interaction(self, interaction: nextcord.Interaction):
        """Handle interactions with this dashboard"""
        component_id = interaction.data.get('custom_id')
        
        if not component_id or component_id not in self.registered_handlers:
            logger.warning(f"No handler registered for component {component_id}")
            await interaction.response.send_message("This button doesn't do anything yet!", ephemeral=True)
            return
            
        handler = self.registered_handlers[component_id]
        await handler(interaction)
    
    async def create_embed(self):
        """Creates the dashboard embed using the build_embed method.
           Requires data to be fetched beforehand.
        """
        # Fetch data just before building embed
        data = await self.fetch_dashboard_data()
        
        return await self.build_embed(data)

    async def create_view(self):
        """Creates the dashboard view using the build_view method.
           Requires data to be fetched beforehand.
        """
        # Fetch data just before building view
        # NOTE: Data should ideally be fetched once per display/refresh cycle
        data = await self.fetch_dashboard_data()

        return await self.build_view(data)
    
    async def display_dashboard(self):
        """Display or update the dashboard in the channel"""
        try:
            if not self.initialized or not self.data_service: # Ensure data service is available
                logger.error(f"Attempted to display uninitialized or misconfigured dashboard: {self.dashboard_id}")
                return None
                
            # Fetch data before creating embed/view
            data = await self.fetch_dashboard_data()
            if data is None: # Check if fetch failed critically
                 logger.error(f"Failed to fetch data for dashboard {self.dashboard_id}. Aborting display.")
                 # Optionally display an error state on the dashboard
                 return None
            logger.debug(f"Fetched data for {self.dashboard_id}")
            # --- END Data Fetch ---
            
            # Get channel
            channel = await self.get_channel() # Inherited from Base
            if not channel:
                logger.error(f"Channel {self.channel_id} not found for {self.dashboard_id}")
                return None
                
            # Create embed and view (using the new methods that call build_embed/build_view with fetched data)
            # Note: build_embed/build_view now receive data directly
            embed = await self.build_embed(data) 
            view = await self.build_view(data)
            
            # Update existing message or send new one
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=view)
                except (nextcord.NotFound, nextcord.HTTPException) as e:
                    logger.warning(f"Failed to edit message {self.message_id} (likely deleted): {e}. Sending new message.")
                    self.message = await channel.send(embed=embed, view=view)
                    self.message_id = self.message.id
            elif self.message_id:
                try:
                    self.message = await channel.fetch_message(self.message_id)
                    await self.message.edit(embed=embed, view=view)
                except (nextcord.NotFound, nextcord.HTTPException) as e:
                    logger.warning(f"Failed to fetch/edit message {self.message_id} (likely deleted): {e}. Sending new message.")
                    self.message = await channel.send(embed=embed, view=view)
                    self.message_id = self.message.id
            else:
                # No existing message, create new one
                self.message = await channel.send(embed=embed, view=view)
                self.message_id = self.message.id
                
            # Update message_id in database
            if self.message_id:
                try:
                    # TODO: Ensure service_factory exists and is the right way to get repo
                    if hasattr(self.bot, 'service_factory'):
                         dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
                         if dashboard_repo:
                             await dashboard_repo.update_dashboard(self.dashboard_id, {'message_id': self.message_id})
                         else:
                             logger.warning("Dashboard repository service not found via service_factory.")
                    else:
                         logger.warning("Bot has no service_factory attribute.")
                except Exception as e:
                    logger.error(f"Error updating message_id in database: {e}")
                
            return self.message
            
        except Exception as e:
            logger.error(f"Error displaying dashboard {self.dashboard_id}: {e}", exc_info=True)
            return None
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info(f"Cleaning up dashboard {self.dashboard_id}")
    
    # --- Methods moved/adapted from DashboardBuilderService --- 

    async def build_embed(self, data: Dict[str, Any]) -> nextcord.Embed:
        """Build an embed from configuration and data."""
        try:
            # Basic embed properties from self.config loaded during initialization
            title = self.config.get('title', self.title) # Use self.title as fallback
            description = self.config.get('description', self.description) # Use self.description as fallback
            color = self.config.get('color', 0x3498db)
            
            if isinstance(color, str) and color.startswith('0x'):
                try:
                    color = int(color, 16)
                except ValueError:
                    logger.warning(f"Invalid color format in config: {color}. Using default.")
                    color = 0x3498db
                
            embed = nextcord.Embed(
                title=title,
                description=description,
                color=color
            )
            
            # Add timestamp
            embed.timestamp = datetime.now()
            
            # Add footer
            footer_config = self.config.get('footer', {})
            if footer_config:
                embed.set_footer(
                    text=footer_config.get('text', 'HomeLab Discord Bot'),
                    icon_url=footer_config.get('icon_url')
                )
            else: # Apply standard footer if none configured
                self.apply_standard_footer(embed)
                
            # Add author
            author_config = self.config.get('author', {})
            if author_config:
                embed.set_author(
                    name=author_config.get('name'),
                    url=author_config.get('url'),
                    icon_url=author_config.get('icon_url')
                )
                
            # Add components defined in config
            component_configs = self.config.get('components', [])
            for component_config in component_configs:
                # Filter for components that render to embed (logic might vary)
                # Assuming components meant for embed have a specific property or type
                # For now, attempt to render all, let component decide
                await self.add_component_to_embed(embed, component_config, data)
                
            return embed
            
        except Exception as e:
            logger.error(f"Error building embed for dashboard {self.dashboard_id}: {e}", exc_info=True)
            # Return a minimal error embed (inherited method)
            return self.create_error_embed(f"Error building embed: {str(e)}", title="Embed Error")
            
    async def add_component_to_embed(self, embed: nextcord.Embed, component_config: Dict[str, Any], data: Dict[str, Any]):
        """Add a component representation to an embed."""
        if not self.component_registry:
            logger.error("Component Registry not available in add_component_to_embed")
            return
            
        component_type = component_config.get('type')
        if not component_type:
            logger.warning(f"Component config missing 'type': {component_config}")
            return
            
        component_impl_class = self.component_registry.get_component(component_type)
        
        if not component_impl_class:
            logger.error(f"Component type not found in registry: {component_type}")
            return
            
        try:
            # Create component instance and render to embed
            component = component_impl_class(self.bot, component_config)
            # Check if the component has the render_to_embed method
            if hasattr(component, 'render_to_embed') and callable(component.render_to_embed):
                await component.render_to_embed(embed, data, component_config.get('config', {}))
            else:
                # logger.debug(f"Component type {component_type} does not render to embed.")
                pass # Not all components render to embed
        except Exception as e:
            logger.error(f"Error rendering component {component_type} to embed: {e}", exc_info=True)

    async def build_view(self, data: Dict[str, Any]) -> Optional[nextcord.ui.View]:
        """Build a view from configuration and data."""
        try:
            # Check if there are interactive components defined in config
            interactive_components = self.config.get('interactive_components', []) # IDs of components to add
            component_configs = self.config.get('components', []) # Full definitions
            
            if not interactive_components or not component_configs:
                # logger.debug(f"No interactive components defined for dashboard {self.dashboard_id}")
                return None # No view needed if no interactive components
                
            # Create view
            view = nextcord.ui.View(timeout=None)
            
            # Add components to view based on interactive_components list
            for component_id in interactive_components:
                # Find the full config for this component ID
                component_config = next((c for c in component_configs if c.get('id') == component_id), None)
                        
                if not component_config:
                    logger.warning(f"Interactive component config not found in 'components' list: {component_id} for dashboard {self.dashboard_id}")
                    continue
                    
                # Create and add component to view
                await self.add_component_to_view(view, component_config, data)
            
            # Only return view if items were actually added
            if len(view.children) > 0:    
                return view
            else:
                logger.debug(f"View built but no components added for dashboard {self.dashboard_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error building view for dashboard {self.dashboard_id}: {e}", exc_info=True)
            return None # Return None on error
            
    async def add_component_to_view(self, view: nextcord.ui.View, component_config: Dict[str, Any], data: Dict[str, Any]):
        """Add a component to a view."""
        if not self.component_registry:
            logger.error("Component Registry not available in add_component_to_view")
            return
            
        component_type = component_config.get('type')
        if not component_type:
            logger.warning(f"Component config missing 'type': {component_config}")
            return
            
        component_impl_class = self.component_registry.get_component(component_type)
        
        if not component_impl_class:
            logger.error(f"Component type not found in registry: {component_type}")
            return
            
        try:
            # Create component instance and add to view
            component = component_impl_class(self.bot, component_config)
            component.dashboard_id = self.dashboard_id # Assign dashboard ID for context
            # Check if the component has the add_to_view method
            if hasattr(component, 'add_to_view') and callable(component.add_to_view):
                await component.add_to_view(view, data, component_config.get('config', {}))
            else:
                logger.warning(f"Component type {component_type} does not have add_to_view method.")
                
        except Exception as e:
            logger.error(f"Error adding component {component_type} to view: {e}", exc_info=True)
            
    # --- Original methods below (load_components, display_dashboard etc remain largely the same) --- 

    # ... (load_dashboard_definition, load_components_from_database, etc.) ...
    # ... (handle_interaction, cleanup etc.) ...
    # Note: load_components_from_database might be less relevant if config defines everything?
    # Note: display_dashboard now calls the overridden create_embed/create_view
    
    # Removed load_components (superseded by config loading + component registry)
    # async def load_components(self):
    #     """Load components for this dashboard"""
    #     ...

    # ... (rest of the methods like cleanup, handle_interaction etc. are likely okay) ... 

    async def fetch_dashboard_data(self) -> Optional[Dict[str, Any]]:
        """Fetches data required for this dashboard using the DashboardDataService."""
        if not self.data_service:
            logger.error(f"DashboardDataService not available for dashboard {self.dashboard_id}")
            return None # Indicate critical failure
            
        data_sources = self.config.get('data_sources', {})
        if not data_sources:
            logger.debug(f"No data sources defined for dashboard {self.dashboard_id}")
            return {} # Return empty dict if no sources defined
            
        try:
            fetched_data = await self.data_service.fetch_data(data_sources)
            return fetched_data
        except Exception as e:
            logger.error(f"Error fetching dashboard data via service for {self.dashboard_id}: {e}", exc_info=True)
            return None # Indicate critical failure
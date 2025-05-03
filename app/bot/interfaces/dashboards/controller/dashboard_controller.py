import nextcord
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# TODO: Need access to ComponentRegistry, potentially passed during initialization or via bot
# from app.bot.core.registries.component_registry import ComponentRegistry 

class DashboardController:
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
        self.bot = kwargs.get('bot')
        self.message_id = kwargs.get('message_id', None)
        self.message: Optional[nextcord.Message] = None
        self.initialized = False
        self.rate_limits = {}
        
        # Dependencies (to be initialized)
        self.component_registry = None 
        self.data_service = None # Renamed from builder service
        
        logger.info(f"Initialized universal dashboard controller for {dashboard_type} dashboard {self.dashboard_id}")
    
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
        # await self.load_dashboard_definition() # This loads self.config, self.title etc.
        
        # Register standard handlers
        self.register_standard_handlers()
        
        self.initialized = True
        logger.info(f"Dashboard {self.dashboard_id} initialization complete")
        return True
    
    # async def load_dashboard_definition(self): # <-- COMMENT OUT METHOD
    #     """
    #     Load dashboard definition from database
    #     This is the key method that makes the controller flexible
    #     [OBSOLETE] Config is now passed via __init__
    #     """
    #     logger.info(f"Loading definition for {self.dashboard_type} dashboard {self.dashboard_id}")
    #     
    #     try:
    #         # Get dashboard repository from service factory
    #         dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
    #         if not dashboard_repo:
    #             raise ValueError("Dashboard repository service not available")
    #         
    #         # Load dashboard configuration from database
    #         dashboard = await dashboard_repo.get_dashboard_by_id(self.dashboard_id)
    #         if not dashboard:
    #             # Try to find by channel ID + type
    #             dashboard = await dashboard_repo.get_dashboard_by_channel_and_type(
    #                 self.channel_id, self.dashboard_type
    #             )
    #         
    #         if not dashboard:
    #             logger.warning(f"No dashboard found for ID {self.dashboard_id}, creating default")
    #             # Create a default dashboard if not found
    #             await self.create_default_dashboard()
    #             return
    #         
    #         # Load components from the database
    #         await self.load_components_from_database(dashboard)
    #         
    #         # Update properties from database
    #         self.title = dashboard.title or self.title
    #         self.description = dashboard.description or self.description
    #         self.config = dashboard.config or self.config
    #         self.message_id = dashboard.message_id or self.message_id
    #         
    #         logger.info(f"Loaded dashboard definition for {self.dashboard_id} from database")
    #         
    #     except Exception as e:
    #         logger.error(f"Error loading dashboard definition from database: {e}")
    #         # Create a default dashboard if loading fails
    #         await self.create_default_dashboard()
    
    # async def load_components_from_database(self, dashboard): # <-- COMMENT OUT METHOD
    #     """Load components for a dashboard from the database
    #     [OBSOLETE] Components are now defined within the config JSON
    #     """
    #     try:
    #         # Load components through the repository
    #         components = await self.bot.service_factory.get_service('dashboard_repository').get_components_for_dashboard(dashboard.id)
    #         
    #         for component in components:
    #             # Process each component based on its type
    #             if component.component_type == 'button':
    #                 self.register_button(
    #                     component.custom_id,
    #                     component.config.get('label', 'Button'),
    #                     component.config.get('style', 'primary'),
    #                     component.config.get('emoji'),
    #                     component.config.get('row', 0),
    #                     component.config.get('disabled', False)
    #                 )
    #             elif component.component_type == 'embed':
    #                 self.register_embed(
    #                     component.custom_id,
    #                     component.config.get('title'),
    #                     component.config.get('description'),
    #                     component.config.get('color'),
    #                     component.config.get('fields', []),
    #                     component.config.get('footer')
    #                 )
    #             # Add more component types as needed
    #             
    #         logger.info(f"Loaded {len(components)} components for dashboard {dashboard.id}")
    #         
    #     except Exception as e:
    #         logger.error(f"Error loading components from database: {e}")
    
    # async def create_default_dashboard(self): # <-- KEEP FOR NOW? Could be useful fallback if config is empty.
    #     """Create a default dashboard configuration"""
    #     logger.info(f"Creating default dashboard for {self.dashboard_type}")
    #     
    #     # Create a basic embed
    #     self.register_embed(
    #         "main_embed",
    #         f"{self.dashboard_type.capitalize()} Dashboard",
    #         "This dashboard was created with default settings",
    #         0x3498db,  # Blue color
    #         []  # No fields
    #     )
    #     
    #     # Create a refresh button
    #     self.register_button(
    #         "refresh_button",
    #         "Refresh",
    #         "secondary",
    #         "🔄",
    #         0,  # Row 0
    #         False  # Not disabled
    #     )
    #     
    #     # Register the refresh handler
    #     self.register_handler("refresh_button", self.on_refresh)
    
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
            if not self.initialized: # Simplified check
                logger.error(f"Attempted to display uninitialized dashboard: {self.dashboard_id}")
                # Try to send an error message to the channel?
                channel = await self.get_channel()
                if channel:
                     await channel.send(embed=self.create_error_embed("Dashboard controller not initialized.", title="Display Error"))
                return None

            if not self.data_service:
                logger.error(f"DataService not available for dashboard {self.dashboard_id}")
                channel = await self.get_channel()
                if channel:
                     await channel.send(embed=self.create_error_embed("Data service unavailable.", title="Display Error"))
                return None

            # Fetch data before creating embed/view
            data = await self.fetch_dashboard_data()
            if data is None: # Check if fetch failed critically
                 logger.error(f"Failed to fetch data for dashboard {self.dashboard_id}. Aborting display.")
                 # Display an error state on the dashboard
                 channel = await self.get_channel()
                 if channel:
                     error_embed = self.create_error_embed("Failed to fetch required data.", title="Data Error")
                     # Try to update existing message or send new one
                     await self._send_or_edit(channel, error_embed, None) # Send error embed, no view
                 return None
            logger.debug(f"Fetched data for {self.dashboard_id}")
            # --- END Data Fetch ---

            # Get channel
            channel = await self.get_channel()
            if not channel:
                logger.error(f"Channel {self.channel_id} not found for {self.dashboard_id}")
                return None

            # Create embed and view
            # Build methods now directly use self.config and data
            embed = await self.build_embed(data)
            view = await self.build_view(data) # Returns None if no interactive components

            # Update existing message or send new one
            # Extracted send/edit logic into a helper
            self.message = await self._send_or_edit(channel, embed, view)

            if self.message:
                 self.message_id = str(self.message.id)
                 logger.info(f"Dashboard {self.dashboard_id} displayed/updated. Message ID: {self.message_id}")
            else:
                 logger.error(f"Failed to send or edit dashboard message for {self.dashboard_id}.")
                 self.message_id = None # Ensure message_id is None if sending failed

            # Return the message object (or None if failed)
            return self.message

        except Exception as e:
            logger.error(f"Error displaying dashboard {self.dashboard_id}: {e}", exc_info=True)
            # Try to display error embed
            try:
                channel = await self.get_channel()
                if channel:
                    error_embed = self.create_error_embed(f"An unexpected error occurred: {e}", title="Display Error")
                    await self._send_or_edit(channel, error_embed, None)
            except Exception as inner_e:
                 logger.error(f"Failed to display error embed after another error: {inner_e}")
            return None

    # Helper for sending/editing message
    async def _send_or_edit(self, channel: nextcord.TextChannel, embed: Optional[nextcord.Embed], view: Optional[nextcord.ui.View]) -> Optional[nextcord.Message]:
        """Handles sending a new message or editing an existing one."""
        message_to_return = None
        if self.message:
            try:
                await self.message.edit(embed=embed, view=view)
                message_to_return = self.message
                logger.debug(f"Edited existing message {self.message.id}")
            except (nextcord.NotFound, nextcord.HTTPException) as e:
                logger.warning(f"Failed to edit message {self.message_id} (likely deleted): {e}. Sending new message.")
                self.message = None # Reset message object
                self.message_id = None # Reset message id
                message_to_return = await channel.send(embed=embed, view=view)
        elif self.message_id:
            try:
                # Attempt to fetch the message first before editing
                msg = await channel.fetch_message(int(self.message_id))
                await msg.edit(embed=embed, view=view)
                self.message = msg # Store fetched message object
                message_to_return = msg
                logger.debug(f"Fetched and edited message {self.message_id}")
            except (nextcord.NotFound, nextcord.HTTPException) as e:
                logger.warning(f"Failed to fetch/edit message {self.message_id} (likely deleted): {e}. Sending new message.")
                self.message = None # Reset message object
                self.message_id = None # Reset message id
                message_to_return = await channel.send(embed=embed, view=view)
            except ValueError:
                 logger.error(f"Invalid message_id format stored: {self.message_id}. Sending new message.")
                 self.message = None
                 self.message_id = None
                 message_to_return = await channel.send(embed=embed, view=view)
        else:
            # No existing message, create new one
            logger.debug("Sending new dashboard message.")
            message_to_return = await channel.send(embed=embed, view=view)

        return message_to_return

    async def cleanup(self):
        """Clean up resources"""
        logger.info(f"Cleaning up dashboard {self.dashboard_id}")
        # Clear view items if applicable (view might be None)
        # view = getattr(self, '_last_view', None) # Assuming view is stored if needed
        # if view:
        #      view.stop()
        #      view.clear_items()
        self.initialized = False
        self.message = None # Remove reference

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

    async def get_channel(self) -> Optional[nextcord.TextChannel]:
        """Get the channel for this dashboard"""
        if not self.bot:
            logger.error(f"Dashboard {self.dashboard_id} has no bot reference")
            return None

        try:
            # Ensure channel_id is int
            channel = self.bot.get_channel(int(self.channel_id))
            if isinstance(channel, nextcord.TextChannel):
                return channel
            elif channel:
                logger.warning(f"Channel {self.channel_id} found but is not a TextChannel (Type: {type(channel)}).")
                return None
            else:
                logger.warning(f"Channel {self.channel_id} not found for dashboard {self.dashboard_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting channel for dashboard {self.dashboard_id}: {str(e)}")
            return None

    def apply_standard_footer(self, embed):
        """Apply standard footer to embed."""
        embed.set_footer(text=f"HomeLab Discord Bot • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return embed

    async def check_rate_limit(self, interaction: nextcord.Interaction, action_type, cooldown_seconds=10):
        """Check if an action is rate limited."""
        user_id = interaction.user.id
        current_time = datetime.now().timestamp()

        # Initialize user's rate limits if not exists
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = {}

        # Check if action is on cooldown
        last_use = self.rate_limits[user_id].get(action_type, 0)
        time_diff = current_time - last_use

        if time_diff < cooldown_seconds:
            # Action is rate limited
            remaining = int(cooldown_seconds - time_diff)
            await interaction.response.send_message(
                f"Please wait {remaining} seconds before using this action again.",
                ephemeral=True
            )
            return False

        # Update last use time
        self.rate_limits[user_id][action_type] = current_time
        return True

    def create_error_embed(self, error_message, title="Error", error_code=None):
        """Create a standardized error embed."""
        embed = nextcord.Embed(
            title=f"❌ {title}",
            description=error_message,
            color=0xe74c3c # Red
        )

        if error_code:
            embed.set_footer(text=f"Error Code: {error_code}")
        else:
            # Apply standard footer even to error embeds
            self.apply_standard_footer(embed)

        return embed

    async def refresh(self, interaction: Optional[nextcord.Interaction] = None):
        """Refresh the dashboard display"""
        # Modified to directly call fetch/display as refresh_data is gone
        logger.info(f"Refreshing dashboard {self.dashboard_id}")
        # No separate refresh_data needed if display_dashboard fetches fresh data
        # await self.refresh_data() # Removed call to non-existent method
        return await self.display_dashboard()
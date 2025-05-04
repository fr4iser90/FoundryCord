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
        
        logger.info(f"Initialized dashboard controller for {dashboard_type} dashboard {self.dashboard_id}")
    
    async def initialize(self, bot):
        """Initialize the dashboard controller"""
        self.bot = bot
        
        bot_id = getattr(bot.user, 'id', 'N/A')
        has_factory = hasattr(bot, 'service_factory')
        factory_obj = getattr(bot, 'service_factory', None)
        factory_type = type(factory_obj).__name__
        logger.info(f"[DEBUG controller.initialize] Received bot. Bot ID: {bot_id}, Has service_factory attr: {has_factory}, Factory Object Type: {factory_type}")
        

        # Get Component Registry & Data Service
        try:
            # Use more specific check and logging
            if has_factory and factory_obj is not None:
                 logger.debug(f"[DEBUG controller.initialize] Trying to get services from factory: {factory_obj}")
                 self.component_registry = factory_obj.get_service('component_registry')
                 self.data_service = factory_obj.get_service('dashboard_data_service') 

                 if not self.component_registry:
                     logger.error("[DEBUG controller.initialize] Component Registry service IS NONE within Service Factory.")
                 else:
                     logger.debug(f"[DEBUG controller.initialize] Component Registry obtained: {type(self.component_registry).__name__}")

                 if not self.data_service:
                     logger.error("[DEBUG controller.initialize] DashboardDataService service IS NONE within Service Factory.")
                 else:
                     logger.debug(f"[DEBUG controller.initialize] Data Service obtained: {type(self.data_service).__name__}")

            elif has_factory and factory_obj is None:
                 logger.error("[DEBUG controller.initialize] Service factory attribute EXISTS but IS NONE on bot instance.")
                 return False # Explicitly return False
            else: # Attribute doesn't exist
                 logger.error("[DEBUG controller.initialize] Service factory attribute DOES NOT EXIST on bot instance.")
                 return False # Explicitly return False

            # Check if services were actually retrieved
            if not self.component_registry:
                logger.error("Component Registry not available for DashboardController after factory check.")
                # return False # Decide handling - maybe allow init but log error? For now, let it proceed with error logs.
            if not self.data_service:
                 logger.error("DashboardDataService not available for DashboardController after factory check.")
                 # return False # Decide handling

        except AttributeError as ae:
             # Catch if factory_obj doesn't have get_service
             logger.error(f"[DEBUG controller.initialize] Service Factory ({factory_type}) missing 'get_service' method? Error: {ae}", exc_info=True)
             return False
        except Exception as e:
            logger.error(f"[DEBUG controller.initialize] Error getting services/registries: {e}", exc_info=True)
            return False
            
        # Load dashboard definition from database
        # await self.load_dashboard_definition() # This loads self.config, self.title etc.
        
        # Register standard handlers
        self.register_standard_handlers()
        
        self.initialized = True
        logger.info(f"Dashboard {self.dashboard_id} initialization complete (Services might be missing).") # Adjusted log
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
        # --- ADD DEBUG LOG ---
        logger.debug(f"[{self.dashboard_id}] display_dashboard: Method started.")
        # --- END DEBUG LOG ---
        try:
            if not self.initialized:
                logger.error(f"[{self.dashboard_id}] display_dashboard: Attempted to display uninitialized dashboard.")
                # Try to send an error message to the channel?
                channel = await self.get_channel()
                if channel:
                     await channel.send(embed=self.create_error_embed("Dashboard controller not initialized.", title="Display Error"))
                return None

            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Checking data_service...")
            # --- END DEBUG LOG ---
            if not self.data_service:
                logger.error(f"[{self.dashboard_id}] display_dashboard: DataService not available.")
                channel = await self.get_channel()
                if channel:
                     await channel.send(embed=self.create_error_embed("Data service unavailable.", title="Display Error"))
                return None
            logger.debug(f"[{self.dashboard_id}] display_dashboard: DataService check passed.")

            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling fetch_dashboard_data...")
            # --- END DEBUG LOG ---
            data = await self.fetch_dashboard_data()
            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] display_dashboard: fetch_dashboard_data returned: {data is not None}")
            # --- END DEBUG LOG ---

            if data is None: # Check if fetch failed critically
                 logger.error(f"[{self.dashboard_id}] display_dashboard: Failed to fetch data. Aborting display.")
                 # Display an error state on the dashboard
                 channel = await self.get_channel()
                 if channel:
                     error_embed = self.create_error_embed("Failed to fetch required data.", title="Data Error")
                     # Try to update existing message or send new one
                     await self._send_or_edit(channel, error_embed, None) # Send error embed, no view
                 return None
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Data fetched successfully.")
            # --- END Data Fetch ---

            # Get channel
            channel = await self.get_channel()
            if not channel:
                logger.error(f"[{self.dashboard_id}] display_dashboard: Channel {self.channel_id} not found.")
                return None

            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling build_embed...")
            # --- END DEBUG LOG ---
            embed = await self.build_embed(data)
            # --- ADD DEBUG LOG ---
            embed_type = type(embed).__name__ if embed else 'None'
            logger.debug(f"[{self.dashboard_id}] display_dashboard: build_embed returned type: {embed_type}")
            # --- END DEBUG LOG ---

            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling build_view...")
            # --- END DEBUG LOG ---
            view = await self.build_view(data) # Returns None if no interactive components
            # --- ADD DEBUG LOG ---
            view_type = type(view).__name__ if view else 'None'
            logger.debug(f"[{self.dashboard_id}] display_dashboard: build_view returned type: {view_type}")
            # --- END DEBUG LOG ---

            # Update existing message or send new one
            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling _send_or_edit...")
            # --- END DEBUG LOG ---
            self.message = await self._send_or_edit(channel, embed, view)
            # --- ADD DEBUG LOG ---
            msg_id = self.message.id if self.message else 'None'
            logger.debug(f"[{self.dashboard_id}] display_dashboard: _send_or_edit returned message with ID: {msg_id}")
            # --- END DEBUG LOG ---

            if self.message:
                 self.message_id = str(self.message.id)
                 logger.info(f"[{self.dashboard_id}] Dashboard displayed/updated. Message ID: {self.message_id}")
            else:
                 logger.error(f"[{self.dashboard_id}] Failed to send or edit dashboard message.")
                 self.message_id = None # Ensure message_id is None if sending failed

            # Return the message object (or None if failed)
            return self.message

        except Exception as e:
            logger.error(f"[{self.dashboard_id}] Error in display_dashboard: {e}", exc_info=True)
            # Try to display error embed
            try:
                channel = await self.get_channel()
                if channel:
                    error_embed = self.create_error_embed(f"An unexpected error occurred: {e}", title="Display Error")
                    await self._send_or_edit(channel, error_embed, None)
            except Exception as inner_e:
                 logger.error(f"[{self.dashboard_id}] Failed to display error embed after another error: {inner_e}")
            return None

    # Helper for sending/editing message
    async def _send_or_edit(self, channel: nextcord.TextChannel, embed: Optional[nextcord.Embed], view: Optional[nextcord.ui.View]) -> Optional[nextcord.Message]:
        """Handles sending a new message or editing an existing one."""
        # --- ADD DEBUG LOG ---
        current_msg_id = self.message.id if self.message else self.message_id
        logger.debug(f"[{self.dashboard_id}] _send_or_edit: Started. Channel: {channel.id}, Current Msg Obj: {self.message is not None}, Current Msg ID: {current_msg_id}, Has Embed: {embed is not None}, Has View: {view is not None}")
        # --- END DEBUG LOG ---
        message_to_return = None
        if self.message:
            try:
                # --- ADD DEBUG LOG ---
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: Attempting to edit existing message object {self.message.id}...")
                # --- END DEBUG LOG ---
                await self.message.edit(embed=embed, view=view)
                message_to_return = self.message
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: Edited existing message object {self.message.id} successfully.")
            except (nextcord.NotFound, nextcord.HTTPException) as e:
                logger.warning(f"[{self.dashboard_id}] _send_or_edit: Failed to edit message object {self.message_id}: {e}. Sending new message.")
                self.message = None # Reset message object
                self.message_id = None # Reset message id
                try:
                     # --- ADD DEBUG LOG ---
                     logger.debug(f"[{self.dashboard_id}] _send_or_edit: Attempting to send new message after edit failure...")
                     # --- END DEBUG LOG ---
                     message_to_return = await channel.send(embed=embed, view=view)
                     logger.debug(f"[{self.dashboard_id}] _send_or_edit: Sent new message (ID: {message_to_return.id}) after edit failure.")
                except Exception as send_err:
                     logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send new message after edit failure: {send_err}", exc_info=True)
        elif self.message_id:
            try:
                # --- ADD DEBUG LOG ---
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: Attempting to fetch message {self.message_id}...")
                # --- END DEBUG LOG ---
                msg = await channel.fetch_message(int(self.message_id))
                # --- ADD DEBUG LOG ---
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: Fetched message {self.message_id}. Attempting to edit...")
                # --- END DEBUG LOG ---
                await msg.edit(embed=embed, view=view)
                self.message = msg # Store fetched message object
                message_to_return = msg
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: Fetched and edited message {self.message_id} successfully.")
            except (nextcord.NotFound, nextcord.HTTPException) as e:
                logger.warning(f"[{self.dashboard_id}] _send_or_edit: Failed to fetch/edit message {self.message_id}: {e}. Sending new message.")
                self.message = None # Reset message object
                self.message_id = None # Reset message id
                try:
                    # --- ADD DEBUG LOG ---
                    logger.debug(f"[{self.dashboard_id}] _send_or_edit: Attempting to send new message after fetch/edit failure...")
                    # --- END DEBUG LOG ---
                    message_to_return = await channel.send(embed=embed, view=view)
                    logger.debug(f"[{self.dashboard_id}] _send_or_edit: Sent new message (ID: {message_to_return.id}) after fetch/edit failure.")
                except Exception as send_err:
                    logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send new message after fetch/edit failure: {send_err}", exc_info=True)
            except ValueError:
                 logger.error(f"[{self.dashboard_id}] _send_or_edit: Invalid message_id format stored: {self.message_id}. Sending new message.")
                 self.message = None
                 self.message_id = None
                 try:
                    # --- ADD DEBUG LOG ---
                    logger.debug(f"[{self.dashboard_id}] _send_or_edit: Attempting to send new message after invalid ID format...")
                    # --- END DEBUG LOG ---
                    message_to_return = await channel.send(embed=embed, view=view)
                    logger.debug(f"[{self.dashboard_id}] _send_or_edit: Sent new message (ID: {message_to_return.id}) after invalid ID format.")
                 except Exception as send_err:
                     logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send new message after invalid ID format: {send_err}", exc_info=True)
        else:
            # No existing message, create new one
            try:
                # --- ADD DEBUG LOG ---
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: No message ID found. Attempting to send new message...")
                # --- END DEBUG LOG ---
                message_to_return = await channel.send(embed=embed, view=view)
                logger.debug(f"[{self.dashboard_id}] _send_or_edit: Sent new message (ID: {message_to_return.id}) successfully.")
            except Exception as send_err:
                logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send initial message: {send_err}", exc_info=True)

        # --- ADD DEBUG LOG ---
        return_msg_id = message_to_return.id if message_to_return else 'None'
        logger.debug(f"[{self.dashboard_id}] _send_or_edit: Finished. Returning message object with ID: {return_msg_id}")
        # --- END DEBUG LOG ---
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
            logger.error(f"[{self.dashboard_id}] Component Registry not available in add_component_to_embed")
            return

        # --- MODIFIED: Get component_key instead of type ---
        component_key = component_config.get('component_key')
        if not component_key:
            instance_id = component_config.get('instance_id', 'N/A')
            logger.warning(f"[{self.dashboard_id}] Component config (instance_id: {instance_id}) missing 'component_key': {component_config}")
            return
        # --- END MODIFICATION ---

        try:
            # --- ADDED: Get type from registry using the key ---
            # Assuming ComponentRegistry has a method to get the type based on the key
            # This might need adjustment depending on the actual ComponentRegistry implementation
            if not hasattr(self.component_registry, 'get_type_by_key'):
                 logger.error(f"[{self.dashboard_id}] ComponentRegistry is missing the required 'get_type_by_key' method.")
                 # Fallback or alternative lookup might be needed here
                 # For now, we cannot proceed without the type.
                 return

            component_type = self.component_registry.get_type_by_key(component_key)
            if not component_type:
                logger.error(f"[{self.dashboard_id}] Component type not found in registry for key: {component_key}")
                return
            logger.debug(f"[{self.dashboard_id}] Resolved component key '{component_key}' to type '{component_type}'.")
            # --- END ADDED SECTION ---

            # --- MODIFIED: Use get_component_class ---
            component_impl_class = self.component_registry.get_component_class(component_type)
            # --- END MODIFICATION ---

            if not component_impl_class:
                # This case should be less likely now if get_type_by_key worked
                logger.error(f"[{self.dashboard_id}] Component implementation class not found in registry for type: {component_type} (from key: {component_key})")
                return

            # Create component instance and render to embed
            # Pass the original component_config which contains instance_id, key, settings
            component = component_impl_class(self.bot, component_config)
            # Check if the component has the render_to_embed method
            if hasattr(component, 'render_to_embed') and callable(component.render_to_embed):
                # Pass component_config (contains instance_id, key, settings) and fetched data
                await component.render_to_embed(embed, data, component_config) # Pass config dict
            else:
                # logger.debug(f"Component type {component_type} does not render to embed.")
                pass # Not all components render to embed

        except Exception as e:
            logger.error(f"[{self.dashboard_id}] Error rendering component (key: {component_key}, type: {component_type}) to embed: {e}", exc_info=True)

    async def build_view(self, data: Dict[str, Any]) -> Optional[nextcord.ui.View]:
        """Build a view from configuration and data."""
        try:
            interactive_components_ids = self.config.get('interactive_components', []) # List of instance_ids
            component_configs = self.config.get('components', []) # Full definitions list

            if not interactive_components_ids or not component_configs:
                return None

            view = nextcord.ui.View(timeout=None)

            # Add components to view based on interactive_components list
            for instance_id_to_add in interactive_components_ids:
                # Find the full config using instance_id
                # --- ENSURE THIS LINE USES 'instance_id' ---
                component_config = next((c for c in component_configs if c.get('instance_id') == instance_id_to_add), None)
                # --- END ENSURE ---

                if not component_config:
                    logger.warning(f"Interactive component config not found for instance_id '{instance_id_to_add}' in 'components' list for dashboard {self.dashboard_id}")
                    continue

                # Create and add component to view
                await self.add_component_to_view(view, component_config, data)

            if len(view.children) > 0:
                return view
            else:
                logger.debug(f"View built but no components added for dashboard {self.dashboard_id}")
                return None

        except Exception as e:
            logger.error(f"Error building view for dashboard {self.dashboard_id}: {e}", exc_info=True)
            return None
            
    async def add_component_to_view(self, view: nextcord.ui.View, component_config: Dict[str, Any], data: Dict[str, Any]):
        """Add a component to a view."""
        if not self.component_registry:
            logger.error(f"[{self.dashboard_id}] Component Registry not available in add_component_to_view")
            return

        # --- MODIFIED: Get component_key instead of type ---
        component_key = component_config.get('component_key')
        if not component_key:
            instance_id = component_config.get('instance_id', 'N/A')
            logger.warning(f"[{self.dashboard_id}] Component config (instance_id: {instance_id}) missing 'component_key': {component_config}")
            return
        # --- END MODIFICATION ---

        try:
            # --- ADDED: Get type from registry using the key ---
            if not hasattr(self.component_registry, 'get_type_by_key'):
                 logger.error(f"[{self.dashboard_id}] ComponentRegistry is missing the required 'get_type_by_key' method.")
                 return
            component_type = self.component_registry.get_type_by_key(component_key)
            if not component_type:
                logger.error(f"[{self.dashboard_id}] Component type not found in registry for key: {component_key}")
                return
            logger.debug(f"[{self.dashboard_id}] Resolved component key '{component_key}' to type '{component_type}'.")
            # --- END ADDED SECTION ---

            # --- MODIFIED: Use get_component_class ---
            component_impl_class = self.component_registry.get_component_class(component_type)
            # --- END MODIFICATION ---

            if not component_impl_class:
                logger.error(f"[{self.dashboard_id}] Component implementation class not found in registry for type: {component_type} (from key: {component_key})")
                return

            # Create component instance and add to view
            component = component_impl_class(self.bot, component_config)
            component.dashboard_id = self.dashboard_id # Assign dashboard ID for context
            # Check if the component has the add_to_view method
            if hasattr(component, 'add_to_view') and callable(component.add_to_view):
                 # Pass component_config (contains instance_id, key, settings) and fetched data
                await component.add_to_view(view, data, component_config) # Pass config dict
            else:
                logger.warning(f"Component type {component_type} does not have add_to_view method.")

        except Exception as e:
            logger.error(f"[{self.dashboard_id}] Error adding component (key: {component_key}, type: {component_type}) to view: {e}", exc_info=True)
            
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
        # --- ADD DEBUG LOG ---
        logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Method started.")
        # --- END DEBUG LOG ---
        if not self.data_service:
            logger.error(f"[{self.dashboard_id}] fetch_dashboard_data: DashboardDataService not available.")
            return None # Indicate critical failure
            
        data_sources = self.config.get('data_sources', {})
        # --- ADD DEBUG LOG ---
        logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Configured data sources: {data_sources}")
        # --- END DEBUG LOG ---
        if not data_sources:
            logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: No data sources defined.")
            return {} # Return empty dict if no sources defined
            
        try:
            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Calling data_service.fetch_data...")
            # --- END DEBUG LOG ---
            fetched_data = await self.data_service.fetch_data(data_sources)
            # --- ADD DEBUG LOG ---
            logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Data fetched successfully. Keys: {list(fetched_data.keys()) if fetched_data else 'None'}")
            # --- END DEBUG LOG ---
            return fetched_data
        except Exception as e:
            logger.error(f"[{self.dashboard_id}] fetch_dashboard_data: Error fetching data via service: {e}", exc_info=True)
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
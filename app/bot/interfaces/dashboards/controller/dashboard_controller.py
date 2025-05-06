import nextcord
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

# Interface Imports
from app.bot.application.interfaces.bot import Bot as BotInterface
from app.bot.application.interfaces.service_factory import ServiceFactory as ServiceFactoryInterface
from app.bot.application.interfaces.component_registry import ComponentRegistry as ComponentRegistryInterface
from app.bot.application.services.dashboard.dashboard_data_service import DashboardDataService

from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

# TODO: Need access to ComponentRegistry, potentially passed during initialization or via bot
# from app.bot.core.registries.component_registry import ComponentRegistry 

class DashboardController:
    """
    Dashboard controller that handles all dashboard types
    through configuration rather than inheritance
    """
    
    def __init__(self, 
                 dashboard_id: str, 
                 channel_id: int, 
                 dashboard_type: str,
                 bot, # No type hint for BotInterface
                 component_registry, # No type hint for ComponentRegistryInterface
                 data_service: 'DashboardDataService', # Type hint for data_service can remain as per TODO
                 **kwargs):
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
        self.bot = bot # Injected
        self.message_id = kwargs.get('message_id', None)
        self.message: Optional[nextcord.Message] = None
        self.initialized = False
        self.rate_limits = {}
        
        # Dependencies (Injected)
        self.component_registry = component_registry
        self.data_service = data_service
        
        logger.debug(f"Initialized dashboard controller for {dashboard_type} dashboard {self.dashboard_id} with injected dependencies.")
    
    async def initialize(self): # Removed bot parameter, as it's injected in __init__
        """Initialize the dashboard controller"""
        # self.bot is already set from __init__
        
        # Dependencies (component_registry, data_service) are now injected via __init__
        # So, no need to fetch them from bot.service_factory here.

        if not self.bot:
            logger.error(f"[{self.dashboard_id}] Bot instance not available during initialization.")
            return False
        if not self.component_registry:
            logger.error(f"[{self.dashboard_id}] Component Registry not available during initialization.")
            # Decide handling - for now, let it proceed but log error.
            # Depending on strictness, could return False here.
        if not self.data_service:
            logger.error(f"[{self.dashboard_id}] DashboardDataService not available during initialization.")
            # Decide handling

        # Load dashboard definition from database (if this logic is still needed here)
        # await self.load_dashboard_definition() 
        
        # Register standard handlers
        self.register_standard_handlers()
        
        self.initialized = True
        logger.debug(f"Dashboard {self.dashboard_id} initialization complete.")
        return True
    
    
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
            
            # --- ADDED DEBUG LOG --- #
            logger.debug(f"[{self.dashboard_id}] DEBUG DATA BEFORE BUILD: {data}")
            # --- END DEBUG LOG --- #
            
            # --- END Data Fetch ---

            # Get channel
            channel = await self.get_channel()
            if not channel:
                logger.error(f"[{self.dashboard_id}] display_dashboard: Channel {self.channel_id} not found.")
                return None

            # --- ADDED DEBUG LOG & TRY/EXCEPT --- #
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling build_embed...")
            embed = None
            try:
                embed = await self.build_embed(data)
                embed_type = type(embed).__name__ if embed else 'None'
                logger.debug(f"[{self.dashboard_id}] display_dashboard: build_embed returned type: {embed_type}")
            except Exception as build_embed_err:
                logger.error(f"[{self.dashboard_id}] display_dashboard: Error during build_embed: {build_embed_err}", exc_info=True)
                # Optionally return an error embed here?
                return None # Abort display if build fails
            # --- END DEBUG LOG & TRY/EXCEPT ---

            # --- ADDED DEBUG LOG & TRY/EXCEPT --- #
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling build_view...")
            view = None
            try:
                view = await self.build_view(data)
                view_type = type(view).__name__ if view else 'None'
                logger.debug(f"[{self.dashboard_id}] display_dashboard: build_view returned type: {view_type}")
            except Exception as build_view_err:
                 logger.error(f"[{self.dashboard_id}] display_dashboard: Error during build_view: {build_view_err}", exc_info=True)
                 # If embed exists but view fails, should we still send the embed?
                 # For now, let's abort if view build fails.
                 return None # Abort display if build fails
            # --- END DEBUG LOG & TRY/EXCEPT ---

            # --- Send or Edit Message --- #
            logger.debug(f"[{self.dashboard_id}] display_dashboard: Calling _send_or_edit...")
            message_object = await self._send_or_edit(channel, embed, view)
            # --- END Send or Edit ---

            if message_object:
                # Update internal message ID if changed/set
                if self.message_id != str(message_object.id):
                    logger.debug(f"[{self.dashboard_id}] display_dashboard: Updating internal message ID to {message_object.id}")
                    self.message_id = str(message_object.id)
                
                logger.debug(f"[{self.dashboard_id}] Dashboard displayed/updated. Message ID: {self.message_id}")
                return message_object # Return the message object
            else:
                logger.error(f"[{self.dashboard_id}] display_dashboard: _send_or_edit failed to return a message object.")
                return None

        except Exception as e:
            logger.error(f"[{self.dashboard_id}] display_dashboard: UNEXPECTED error: {e}", exc_info=True)
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

    async def build_embed(self, data: Dict[str, Any]) -> Optional[nextcord.Embed]:
        """
        Builds the main embed for the dashboard by finding the first configured
        embed component and calling its build() method.
        Assumes only one primary embed component per dashboard message.
        """
        if not self.config or 'components' not in self.config:
            logger.warning(f"Dashboard {self.dashboard_id}: Config is missing or has no components key.")
            return self.create_error_embed("Dashboard configuration is missing components.")

        embed_component_config = None
        component_key = None

        # Find the first component definition that resolves to an embed type
        for comp_config in self.config.get('components', []):
            key = comp_config.get('component_key')
            if not key:
                logger.warning(f"Dashboard {self.dashboard_id}: Component config missing 'component_key': {comp_config}")
                continue

            if not self.component_registry:
                 logger.error(f"Dashboard {self.dashboard_id}: Cannot build embed, ComponentRegistry is not available.")
                 return self.create_error_embed("Internal Error: Component Registry unavailable.")

            # Check the type of the component referenced by the key
            definition_wrapper = self.component_registry.get_definition_by_key(key)
            if definition_wrapper and definition_wrapper.get('type') == 'embed':
                 # Found the primary embed component configuration
                 embed_component_config = comp_config
                 component_key = key
                 logger.debug(f"Dashboard {self.dashboard_id}: Found embed component config with key '{key}' and instance_id '{comp_config.get('instance_id')}'")
                 break # Use the first one found

        if not embed_component_config or not component_key:
            logger.warning(f"Dashboard {self.dashboard_id}: No component with type 'embed' found in configuration.")
            # Maybe return None or a default embed indicating no content?
            return None # No embed component defined

        # Get the implementation class for 'embed'
        component_class = self.component_registry.get_component_class('embed')
        if not component_class:
            logger.error(f"Dashboard {self.dashboard_id}: No implementation class registered for component type 'embed'.")
            return self.create_error_embed("Internal Error: Embed component class not found.")

        try:
            # Instantiate the component using the specific instance config from the layout
            # The component's __init__ (via BaseComponent) will fetch the base definition
            # using component_key and merge it with instance settings.
            component_instance = component_class(self.bot, embed_component_config)

            # --- Extract the relevant data for the embed ---
            # Assumption: The first embed component uses the data from the first defined data source.
            embed_data_to_pass = {}
            data_sources_config = self.config.get('data_sources', {})
            if data_sources_config and data: # Ensure config and fetched data exist
                first_data_source_key = next(iter(data_sources_config), None)
                if first_data_source_key and first_data_source_key in data:
                    embed_data_to_pass = data.get(first_data_source_key, {})
                    logger.debug(f"Dashboard {self.dashboard_id}: Extracted data for key '{first_data_source_key}' to pass to embed build.")
                else:
                     logger.warning(f"Dashboard {self.dashboard_id}: First data source key '{first_data_source_key}' not found in fetched data keys: {list(data.keys())}. Passing empty dict to embed.")
            else:
                 logger.debug(f"Dashboard {self.dashboard_id}: No data sources configured or no data fetched. Passing empty dict to embed.")
            # --- End data extraction ---

            # --- Add Log for Extracted Data --- 
            hostname_val = embed_data_to_pass.get('hostname', 'NOT_FOUND')
            cpu_val = embed_data_to_pass.get('cpu_percent', 'NOT_FOUND')
            logger.debug(f"[DIAGNOSTIC Controller - build_embed] Data to pass to embed: Hostname={hostname_val}, CPU={cpu_val}, Full Dict Keys: {list(embed_data_to_pass.keys())}")
            # --- End Log --- 

            # --- MODIFICATION START: Adapt data structure for template --- 
            final_data_for_build = embed_data_to_pass
            if 'items' in embed_data_to_pass and isinstance(embed_data_to_pass['items'], list):
                logger.debug(f"Dashboard {self.dashboard_id}: Adapting data structure: found 'items' key. Renaming to 'projects' for template.")
                # Create a new dict matching the template's expected variable name
                final_data_for_build = {'projects': embed_data_to_pass['items']}
            else:
                logger.debug(f"Dashboard {self.dashboard_id}: Data structure already suitable or no 'items' key found. Passing as is.")
            # --- MODIFICATION END ---

            # Build the embed using the component's own build method
            # --- MODIFIED: Pass the potentially adapted data dictionary ---
            built_embed = component_instance.build(data=final_data_for_build) 

            if not isinstance(built_embed, nextcord.Embed):
                 logger.error(f"Dashboard {self.dashboard_id}: Component {component_key} build() method did not return a nextcord.Embed object.")
                 return self.create_error_embed("Internal Error: Failed to build embed content.")

            # Apply standard footer or dynamic data if needed (optional)
            # Example: self.apply_standard_footer(built_embed)
            # Example: Add dynamic data to description/fields if necessary
            # built_embed.description = f"{built_embed.description}\\nLast updated: {datetime.now()}" # Example dynamic data

            # --- MODIFICATION START: Change log level ---
            logger.debug(f"Dashboard {self.dashboard_id}: Successfully built embed using component {component_key}.")
            # --- MODIFICATION END ---
            return built_embed

        except Exception as e:
            logger.error(f"Dashboard {self.dashboard_id}: Failed to instantiate or build embed component {component_key}: {e}", exc_info=True)
            return self.create_error_embed(f"Error building dashboard content ({component_key}).")

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

        try:

            if not hasattr(self.component_registry, 'get_type_by_key'):
                 logger.error(f"[{self.dashboard_id}] ComponentRegistry is missing the required 'get_type_by_key' method.")
                 return
            component_type = self.component_registry.get_type_by_key(component_key)
            if not component_type:
                logger.error(f"[{self.dashboard_id}] Component type not found in registry for key: {component_key}")
                return
            logger.debug(f"[{self.dashboard_id}] Resolved component key '{component_key}' to type '{component_type}'.")

            component_impl_class = self.component_registry.get_component_class(component_type)


            if not component_impl_class:
                logger.error(f"[{self.dashboard_id}] Component implementation class not found in registry for type: {component_type} (from key: {component_key})")
                return


            logger.debug(f"[DIAGNOSTIC Controller] Config passed to {component_impl_class.__name__} for key '{component_key}' (Instance: {component_config.get('instance_id')}): {component_config}")


            # Create component instance and add to view
            # Pass the **entire instance config** found earlier, which includes component_key, instance_id, and settings
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
            logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Fetching data using data_service...")
            # --- END DEBUG LOG ---
            if not self.data_service:
                logger.error(f"[{self.dashboard_id}] fetch_dashboard_data: DashboardDataService is not initialized.")
                return None
                
            # --- MODIFICATION START: Create and pass context ---
            context = {
                'guild_id': self.guild_id
            }
            logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Passing context: {context}")
            # Pass context to the data service fetch method
            data = await self.data_service.fetch_data(
                data_sources_config=data_sources,
                context=context
            )
            # --- MODIFICATION END ---
            
            # --- ADD DEBUG LOG ---
            data_keys = list(data.keys()) if data else 'None'
            logger.debug(f"[{self.dashboard_id}] fetch_dashboard_data: Data fetched successfully. Keys: {data_keys}")
            # --- END DEBUG LOG ---
            return data
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
            logger.error(f"Error getting channel for dashboard {self.dashboard_id}: {str(e)}", exc_info=True)
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

    async def refresh_data(self):
        """Fetches new data and updates the displayed dashboard message."""
        logger.debug(f"Dashboard {self.dashboard_id}: Starting data refresh.")
        try:
            data = await self.fetch_dashboard_data()
            if data is None:
                logger.error(f"Dashboard {self.dashboard_id}: Failed to fetch data during refresh.")
                # Optionally update display with an error state?
                return

            embed = await self.build_embed(data)
            view = await self.build_view(data)

            if embed is None and view is None:
                 logger.warning(f"Dashboard {self.dashboard_id}: Both embed and view were None after build during refresh. Cannot update.")
                 return

            await self.update_display(embed=embed, view=view)
            # --- MODIFICATION START: Change log level ---
            logger.debug(f"Dashboard {self.dashboard_id}: Successfully refreshed and updated display.")
            # --- MODIFICATION END ---

        except Exception as e:
            logger.error(f"Dashboard {self.dashboard_id}: Unhandled error during refresh_data: {e}", exc_info=True)

    async def update_display(self, embed: Optional[nextcord.Embed], view: Optional[nextcord.ui.View]):
        """Edits the existing dashboard message with the new embed and view."""
        if not self.message_id:
            logger.error(f"Dashboard {self.dashboard_id}: Cannot update display, message_id is not set.")
            return
        if not self.channel_id:
             logger.error(f"Dashboard {self.dashboard_id}: Cannot update display, channel_id is not set.")
             return

        try:
            channel = await self.get_channel()
            if not channel:
                logger.error(f"Dashboard {self.dashboard_id}: Could not find channel {self.channel_id} to update display.")
                return

            # Fetch the existing message
            message = await channel.fetch_message(self.message_id)
            
            # Edit the message
            await message.edit(embed=embed, view=view)
            logger.debug(f"Dashboard {self.dashboard_id}: Successfully edited message {self.message_id} in channel {self.channel_id}.")

        except nextcord.NotFound:
            logger.error(f"Dashboard {self.dashboard_id}: Message {self.message_id} not found in channel {self.channel_id}. Cannot update display. Maybe it was deleted?", exc_info=True)
            # Consider resetting self.message_id or attempting to resend?
        except nextcord.Forbidden:
             logger.error(f"Dashboard {self.dashboard_id}: Bot lacks permissions to edit message {self.message_id} in channel {self.channel_id}.", exc_info=True)
        except Exception as e:
            logger.error(f"Dashboard {self.dashboard_id}: Unexpected error updating display for message {self.message_id}: {e}", exc_info=True)

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
        logger.info(f"Dashboard {self.dashboard_id}: Refresh triggered by interaction.")
        await self.refresh_data() # Call the main refresh logic
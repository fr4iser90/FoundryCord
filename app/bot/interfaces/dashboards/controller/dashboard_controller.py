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
        
        # Keep this initial log, maybe change level if too noisy later
        logger.info(f"Initialized dashboard controller for {dashboard_type} dashboard {self.dashboard_id}")
    
    async def initialize(self, bot):
        """Initialize the dashboard controller"""
        self.bot = bot
        
        # Keep initial check logs for now, might reduce later if stable
        bot_id = getattr(bot.user, 'id', 'N/A')
        has_factory = hasattr(bot, 'service_factory')
        factory_obj = getattr(bot, 'service_factory', None)
        factory_type = type(factory_obj).__name__
        logger.debug(f"[DEBUG controller.initialize] Received bot. Bot ID: {bot_id}, Has service_factory attr: {has_factory}, Factory Object Type: {factory_type}") # Changed to DEBUG
        

        # Get Component Registry & Data Service
        try:
            # Use more specific check and logging
            if has_factory and factory_obj is not None:
                 logger.debug(f"[DEBUG controller.initialize] Trying to get services from factory: {factory_obj}")
                 self.component_registry = factory_obj.get_service('component_registry')
                 self.data_service = factory_obj.get_service('dashboard_data_service') 

                 if not self.component_registry:
                     logger.error("[DEBUG controller.initialize] Component Registry service IS NONE within Service Factory.")
                 # Removed else log for component registry obtained

                 if not self.data_service:
                     logger.error("[DEBUG controller.initialize] DashboardDataService service IS NONE within Service Factory.")
                 # Removed else log for data service obtained

            elif has_factory and factory_obj is None:
                 logger.error("[DEBUG controller.initialize] Service factory attribute EXISTS but IS NONE on bot instance.")
                 return False # Explicitly return False
            else: # Attribute doesn't exist
                 logger.error("[DEBUG controller.initialize] Service factory attribute DOES NOT EXIST on bot instance.")
                 return False # Explicitly return False

            # Keep these checks for now
            if not self.component_registry:
                logger.error("Component Registry not available for DashboardController after factory check.")
            if not self.data_service:
                 logger.error("DashboardDataService not available for DashboardController after factory check.")

        except AttributeError as ae:
             # Catch if factory_obj doesn't have get_service
             # Use the simplified log from previous fix attempt
             logger.error(f"[DEBUG controller.initialize] Service Factory ({factory_type}) missing 'get_service' method?", exc_info=True)
             return False
        except Exception as e:
            logger.error(f"[DEBUG controller.initialize] Error getting services/registries: {e}", exc_info=True)
            return False
            
        # Load dashboard definition from database
        # await self.load_dashboard_definition() # This loads self.config, self.title etc.
        
        # Register standard handlers
        self.register_standard_handlers()
        
        self.initialized = True
        # Keep this completion log
        logger.info(f"Dashboard {self.dashboard_id} initialization complete (Services might be missing).")
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
        # Removed debug log for embed registration
    
    def register_button(self, button_id, label, style="primary", emoji=None, row=0, disabled=False):
        """Register a button configuration"""
        self.registered_buttons[button_id] = {
            'label': label,
            'style': style,
            'emoji': emoji,
            'row': row,
            'disabled': disabled
        }
        # Removed debug log for button registration
    
    def register_handler(self, component_id, handler_func):
        """Register a handler function for a component"""
        self.registered_handlers[component_id] = handler_func
        # Removed debug log for handler registration
    
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
        # Remove entry log
        try:
            if not self.initialized:
                logger.error(f"[{self.dashboard_id}] display_dashboard: Attempted to display uninitialized dashboard.")
                channel = await self.get_channel()
                if channel:
                     await channel.send(embed=self.create_error_embed("Dashboard controller not initialized.", title="Display Error"))
                return None

            # Remove data service check log
            if not self.data_service:
                logger.error(f"[{self.dashboard_id}] display_dashboard: DataService not available.")
                channel = await self.get_channel()
                if channel:
                     await channel.send(embed=self.create_error_embed("Data service unavailable.", title="Display Error"))
                return None
            # Remove data service check passed log

            # Remove calling fetch log
            data = await self.fetch_dashboard_data()
            # Remove fetch returned log

            if data is None: # Check if fetch failed critically
                 logger.error(f"[{self.dashboard_id}] display_dashboard: Failed to fetch data. Aborting display.")
                 channel = await self.get_channel()
                 if channel:
                     error_embed = self.create_error_embed("Failed to fetch required data.", title="Data Error")
                     await self._send_or_edit(channel, error_embed, None) # Send error embed, no view
                 return None
            # Remove data fetched success log

            # Get channel
            channel = await self.get_channel()
            if not channel:
                logger.error(f"[{self.dashboard_id}] display_dashboard: Channel {self.channel_id} not found.")
                return None

            # Remove calling build_embed log
            embed = await self.build_embed(data)
            # Remove build_embed returned log

            # Remove calling build_view log
            view = await self.build_view(data) # Returns None if no interactive components
            # Remove build_view returned log

            # Remove calling _send_or_edit log
            self.message = await self._send_or_edit(channel, embed, view)
            # Remove _send_or_edit returned log

            if self.message:
                 self.message_id = str(self.message.id)
                 logger.info(f"[{self.dashboard_id}] Dashboard displayed/updated. Message ID: {self.message_id}") # Keep INFO log
            else:
                 logger.error(f"[{self.dashboard_id}] Failed to send or edit dashboard message.")
                 self.message_id = None 

            return self.message

        except Exception as e:
            logger.error(f"[{self.dashboard_id}] Error in display_dashboard: {e}", exc_info=True)
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
        # Remove entry log
        message_to_return = None
        if self.message:
            try:
                # Remove attempting edit log
                await self.message.edit(embed=embed, view=view)
                message_to_return = self.message
                # Removed edited success log
            except (nextcord.NotFound, nextcord.HTTPException) as e:
                logger.warning(f"[{self.dashboard_id}] _send_or_edit: Failed to edit message object {self.message_id}: {e}. Sending new message.")
                self.message = None 
                self.message_id = None 
                try:
                     # Remove attempt send log
                     message_to_return = await channel.send(embed=embed, view=view)
                     # Removed sent new message log
                except Exception as send_err:
                     logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send new message after edit failure: {send_err}", exc_info=True)
        elif self.message_id:
            try:
                # Remove attempt fetch log
                msg = await channel.fetch_message(int(self.message_id))
                # Remove fetched log
                await msg.edit(embed=embed, view=view)
                self.message = msg 
                message_to_return = msg
                # Removed fetched and edited success log
            except (nextcord.NotFound, nextcord.HTTPException) as e:
                logger.warning(f"[{self.dashboard_id}] _send_or_edit: Failed to fetch/edit message {self.message_id}: {e}. Sending new message.")
                self.message = None 
                self.message_id = None 
                try:
                    # Remove attempt send log
                    message_to_return = await channel.send(embed=embed, view=view)
                    # Removed sent new message log
                except Exception as send_err:
                    logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send new message after fetch/edit failure: {send_err}", exc_info=True)
            except ValueError:
                 logger.error(f"[{self.dashboard_id}] _send_or_edit: Invalid message_id format stored: {self.message_id}. Sending new message.")
                 self.message = None
                 self.message_id = None
                 try:
                    # Removed attempt send log
                    message_to_return = await channel.send(embed=embed, view=view)
                    # Removed sent new message log
                 except Exception as send_err:
                     logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send new message after invalid ID format: {send_err}", exc_info=True)
        else:
            # No existing message, create new one
            try:
                # Removed attempt send log
                message_to_return = await channel.send(embed=embed, view=view)
                # Removed sent new message log
            except Exception as send_err:
                logger.error(f"[{self.dashboard_id}] _send_or_edit: Failed to send initial message: {send_err}", exc_info=True)

        # Removed finished log
        return message_to_return

    async def cleanup(self):
        """Clean up resources"""
        # Keep info log
        logger.info(f"Cleaning up dashboard {self.dashboard_id}")
        self.initialized = False
        self.message = None 
        # Removed the refresh_data call from cleanup as it seemed odd here

    # --- Methods moved/adapted from DashboardBuilderService --- 

    async def build_embed(self, data: Dict[str, Any]) -> Optional[nextcord.Embed]:
        """
        Builds the main embed for the dashboard by finding the first configured
        embed component and calling its build() method.
        Assumes only one primary embed component per dashboard message.
        """
        # Keep warning logs for config issues
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
                 embed_component_config = comp_config
                 component_key = key
                 # Removed found embed component log
                 break 

        if not embed_component_config or not component_key:
            logger.warning(f"Dashboard {self.dashboard_id}: No component with type 'embed' found in configuration.")
            return None 

        # Keep error logs for missing classes
        component_class = self.component_registry.get_component_class('embed')
        if not component_class:
            logger.error(f"Dashboard {self.dashboard_id}: No implementation class registered for component type 'embed'.")
            return self.create_error_embed("Internal Error: Embed component class not found.")

        try:
            component_instance = component_class(self.bot, embed_component_config)
            built_embed = component_instance.build(data=data) 

            if not isinstance(built_embed, nextcord.Embed):
                 logger.error(f"Dashboard {self.dashboard_id}: Component {component_key} build() method did not return a nextcord.Embed object.")
                 return self.create_error_embed("Internal Error: Failed to build embed content.")

            # Keep success log
            logger.info(f"Dashboard {self.dashboard_id}: Successfully built embed using component {component_key}.")
            return built_embed

        except Exception as e:
            logger.error(f"Dashboard {self.dashboard_id}: Failed to instantiate or build embed component {component_key}: {e}", exc_info=True)
            return self.create_error_embed(f"Error building dashboard content ({component_key}).")

    async def build_view(self, data: Dict[str, Any]) -> Optional[nextcord.ui.View]:
        """Build a view from configuration and data."""
        try:
            interactive_components_ids = self.config.get('interactive_components', []) 
            component_configs = self.config.get('components', []) 

            if not interactive_components_ids or not component_configs:
                return None

            view = nextcord.ui.View(timeout=None)

            for instance_id_to_add in interactive_components_ids:
                component_config = next((c for c in component_configs if c.get('instance_id') == instance_id_to_add), None)
                if not component_config:
                    logger.warning(f"Interactive component config not found for instance_id '{instance_id_to_add}' in 'components' list for dashboard {self.dashboard_id}")
                    continue
                await self.add_component_to_view(view, component_config, data)

            if len(view.children) > 0:
                return view
            else:
                # Removed view built but no components added log
                return None

        except Exception as e:
            logger.error(f"Error building view for dashboard {self.dashboard_id}: {e}", exc_info=True)
            return None
            
    async def add_component_to_view(self, view: nextcord.ui.View, component_config: Dict[str, Any], data: Dict[str, Any]):
        """Add a component to a view."""
        if not self.component_registry:
            logger.error(f"[{self.dashboard_id}] Component Registry not available in add_component_to_view")
            return

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
            # Removed resolved component key log

            component_impl_class = self.component_registry.get_component_class(component_type)
            if not component_impl_class:
                logger.error(f"[{self.dashboard_id}] Component implementation class not found in registry for type: {component_type} (from key: {component_key})")
                return

            # Removed DIAGNOSTIC log about config passed

            component = component_impl_class(self.bot, component_config)
            component.dashboard_id = self.dashboard_id 
            if hasattr(component, 'add_to_view') and callable(component.add_to_view):
                await component.add_to_view(view, data, component_config) 
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
        # Removed entry log
        if not self.data_service:
            logger.error(f"[{self.dashboard_id}] fetch_dashboard_data: DashboardDataService not available.")
            return None 
            
        data_sources = self.config.get('data_sources', {})
        # Removed configured data sources log
        if not data_sources:
            # Removed no data sources log
            return {} 
            
        try:
            # Removed calling data service log
            context_to_pass = {'guild_id': self.guild_id}
            # Removed passing context log
            fetched_data = await self.data_service.fetch_data(data_sources, context=context_to_pass)
            # Removed data fetched success log
            return fetched_data
        except Exception as e:
            logger.error(f"[{self.dashboard_id}] fetch_dashboard_data: Error fetching data via service: {e}", exc_info=True)
            return None 

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
        # Keep info log
        logger.info(f"Refreshing dashboard {self.dashboard_id}")
        return await self.display_dashboard()

    async def refresh_data(self):
        """Fetches new data and updates the displayed dashboard message."""
        # Removed entry log
        try:
            data = await self.fetch_dashboard_data()
            if data is None:
                logger.error(f"Dashboard {self.dashboard_id}: Failed to fetch data during refresh.")
                return

            embed = await self.build_embed(data)
            view = await self.build_view(data)

            if embed is None and view is None:
                 logger.warning(f"Dashboard {self.dashboard_id}: Both embed and view were None after build during refresh. Cannot update.")
                 return

            await self.update_display(embed=embed, view=view)
            # Keep info log
            logger.info(f"Dashboard {self.dashboard_id}: Successfully refreshed and updated display.")

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

            message = await channel.fetch_message(int(self.message_id)) # Ensure message_id is int
            await message.edit(embed=embed, view=view)
            # Removed successful edit log

        except nextcord.NotFound:
            logger.error(f"Dashboard {self.dashboard_id}: Message {self.message_id} not found in channel {self.channel_id}. Cannot update display. Maybe it was deleted?", exc_info=True)
        except nextcord.Forbidden:
             logger.error(f"Dashboard {self.dashboard_id}: Bot lacks permissions to edit message {self.message_id} in channel {self.channel_id}.", exc_info=True)
        except ValueError: # Handle case where self.message_id is not a valid integer
             logger.error(f"Dashboard {self.dashboard_id}: Stored message_id '{self.message_id}' is not a valid integer. Cannot update display.")
        except Exception as e:
            logger.error(f"Dashboard {self.dashboard_id}: Unexpected error updating display for message {self.message_id}: {e}", exc_info=True)

    async def cleanup(self):
        """Clean up resources"""
        # Keep info log
        logger.info(f"Cleaning up dashboard {self.dashboard_id}")
        self.initialized = False
        self.message = None 
        # Removed the refresh_data call from cleanup as it seemed odd here
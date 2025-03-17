import nextcord
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class UniversalDashboardController:
    """
    Universal dashboard controller that handles all dashboard types
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
        
        logger.info(f"Initialized universal dashboard controller for {dashboard_type} dashboard {dashboard_id}")
    
    async def initialize(self, bot):
        """Initialize the dashboard controller"""
        self.bot = bot
        
        # Load dashboard definition from database
        await self.load_dashboard_definition()
        
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
        # Check rate limiting
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
        """Create the main dashboard embed from registered configurations"""
        # Use the first embed as the main one for now
        # In future, multiple embeds could be combined or selected based on config
        if not self.registered_embeds:
            # Default empty embed if none are registered
            return nextcord.Embed(title=self.title, description=self.description, color=0x3498db)
            
        embed_id, embed_config = next(iter(self.registered_embeds.items()))
        
        # Create the embed
        embed = nextcord.Embed(
            title=embed_config.get('title', self.title),
            description=embed_config.get('description', self.description),
            color=embed_config.get('color', 0x3498db)
        )
        
        # Add fields
        for field in embed_config.get('fields', []):
            embed.add_field(
                name=field.get('name', ''),
                value=field.get('value', ''),
                inline=field.get('inline', False)
            )
        
        # Apply standard footer if not specified
        footer_text = None
        footer_icon = None
        
        if embed_config.get('footer'):
            footer_text = embed_config['footer'].get('text')
            footer_icon = embed_config['footer'].get('icon_url')
            
        if not footer_text:
            embed = self.apply_standard_footer(embed)
        else:
            embed.set_footer(text=footer_text, icon_url=footer_icon)
            
        return embed
    
    async def create_view(self):
        """Create the dashboard view with buttons"""
        view = nextcord.ui.View(timeout=None)
        
        # Group buttons by row
        buttons_by_row = {}
        for button_id, button_config in self.registered_buttons.items():
            row = button_config.get('row', 0)
            if row not in buttons_by_row:
                buttons_by_row[row] = []
            buttons_by_row[row].append((button_id, button_config))
        
        # Add buttons to view, sorted by row
        for row in sorted(buttons_by_row.keys()):
            for button_id, button_config in buttons_by_row[row]:
                # Create button
                button_style_name = button_config.get('style', 'primary').lower()
                button_style = getattr(nextcord.ButtonStyle, button_style_name, nextcord.ButtonStyle.primary)
                
                button = nextcord.ui.Button(
                    style=button_style,
                    label=button_config.get('label', 'Button'),
                    emoji=button_config.get('emoji'),
                    custom_id=button_id,
                    disabled=button_config.get('disabled', False),
                    row=row
                )
                
                # Add to view
                view.add_item(button)
        
        return view
    
    async def display_dashboard(self):
        """Display or update the dashboard in the channel"""
        try:
            # Get channel
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Channel {self.channel_id} not found")
                return None
                
            # Create embed and view
            embed = await self.create_embed()
            view = await self.create_view()
            
            # Update existing message or send new one
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=view)
                except Exception as e:
                    # Message was deleted or other error, create new one
                    self.message = await channel.send(embed=embed, view=view)
                    self.message_id = self.message.id
            elif self.message_id:
                try:
                    self.message = await channel.fetch_message(self.message_id)
                    await self.message.edit(embed=embed, view=view)
                except Exception as e:
                    # Message was deleted or other error, create new one
                    self.message = await channel.send(embed=embed, view=view)
                    self.message_id = self.message.id
            else:
                # No existing message, create new one
                self.message = await channel.send(embed=embed, view=view)
                self.message_id = self.message.id
                
            # Update message_id in database
            if self.message_id:
                try:
                    dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
                    if dashboard_repo:
                        await dashboard_repo.update_dashboard(self.dashboard_id, {'message_id': self.message_id})
                except Exception as e:
                    logger.error(f"Error updating message_id in database: {e}")
                
            return self.message
            
        except Exception as e:
            logger.error(f"Error displaying dashboard {self.dashboard_id}: {e}")
            return None
    
    def apply_standard_footer(self, embed):
        """Apply standard footer to embed"""
        embed.set_footer(text=f"HomeLab Discord Bot • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return embed
    
    async def check_rate_limit(self, interaction, action_type, cooldown_seconds=10):
        """Check if an action is rate limited"""
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
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info(f"Cleaning up dashboard {self.dashboard_id}")
    
    async def load_components(self):
        """Load components for this dashboard"""
        try:
            # Get component loader service
            component_loader = self.bot.service_factory.get_service('component_loader')
            if component_loader:
                self.components = await component_loader.load_components_for_dashboard(self.dashboard_id)
                logger.info(f"Loaded {len(self.components)} components for dashboard {self.dashboard_id}")
                return True
            else:
                logger.warning("Component loader service not available")
                return False
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            return False 
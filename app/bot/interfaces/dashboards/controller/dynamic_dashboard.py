from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime
import json
import asyncio
import uuid

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from .base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.components.common.embeds import DashboardEmbed
from app.bot.interfaces.dashboards.components.factories.ui_component_factory import UIComponentFactory
from app.bot.application.services.dashboard.dashboard_service import DashboardService
from app.bot.application.services.dashboard.dashboard_builder import DashboardBuilder


class DynamicDashboardController(BaseDashboardController):
    """Controller for dynamic, configurable dashboards."""
    
    DASHBOARD_TYPE = "dynamic"
    
    def __init__(self, bot, config_id=None):
        super().__init__(bot)
        self.config_id = config_id or str(uuid.uuid4())
        self.config = {}
        self.last_refresh = None
        self.refresh_interval = 300  # Default: 5 minutes
        self.refresh_task = None
        self.dashboard_builder = None
        self.dashboard_repository = None
        self.data = {}
        self.components_cache = None
        self.dashboard = None
        self.dashboard_service = None
        self.channel = None
        self.message = None
        self.components = {}
        self.ui_factory = UIComponentFactory()
    
    async def initialize(self):
        """Initialize from configuration."""
        try:
            # Get required services
            self.dashboard_builder = self.bot.service_factory.get_service('dashboard_builder')
            self.dashboard_repository = self.bot.service_factory.get_service('dashboard_repository')
            
            if not self.dashboard_builder:
                logger.error("Dashboard Builder service not available")
                return False
                
            if not self.dashboard_repository:
                logger.error("Dashboard Repository service not available")
                return False
                
            # Load configuration from repository
            await self.load_config()
            
            # Set up attributes from config
            self.title = self.config.get('title', 'Dynamic Dashboard')
            self.description = self.config.get('description', '')
            self.TITLE_IDENTIFIER = self.title
            
            # Set refresh interval if specified
            if 'refresh_interval' in self.config:
                self.refresh_interval = int(self.config['refresh_interval'])
                
            # Initial data refresh
            await self.refresh_data()
            
            # Start refresh task
            self._start_refresh_task()
            
            self.initialized = True
            logger.info(f"Dynamic dashboard initialized: {self.config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing dynamic dashboard {self.config_id}: {e}")
            return False
    
    async def load_config(self):
        """Load dashboard configuration from repository."""
        try:
            # Get configuration from repository
            self.config = await self.dashboard_repository.get_dashboard_config(self.config_id)
            
            if not self.config:
                logger.error(f"Dashboard configuration not found: {self.config_id}")
                raise ValueError(f"Dashboard configuration not found: {self.config_id}")
                
            logger.debug(f"Loaded dashboard configuration: {self.config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading dashboard configuration {self.config_id}: {e}")
            raise
    
    async def refresh_data(self):
        """Refresh data from data sources."""
        try:
            # Get data from configuration
            if not self.dashboard_builder:
                logger.error("Dashboard Builder service not available for refresh")
                return False
                
            # Fetch data from data sources
            self.data = await self.dashboard_builder.fetch_data_sources(
                self.config.get('data_sources', {})
            )
            
            # Clear components cache so they'll be rebuilt with new data
            self.components_cache = None
            
            # Update last refresh time
            self.last_refresh = datetime.now()
            
            logger.debug(f"Refreshed data for dashboard {self.config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing data for dashboard {self.config_id}: {e}")
            return False
    
    def _start_refresh_task(self):
        """Start the refresh task."""
        if self.refresh_task and not self.refresh_task.done():
            self.refresh_task.cancel()
            
        self.refresh_task = asyncio.create_task(self._refresh_loop())
    
    async def _refresh_loop(self):
        """Periodically refresh dashboard data."""
        try:
            while True:
                # Wait for refresh interval
                await asyncio.sleep(self.refresh_interval)
                
                # Refresh data
                await self.refresh_data()
                
                # Update display
                await self.display_dashboard()
                    
        except asyncio.CancelledError:
            logger.debug(f"Refresh task cancelled for dashboard {self.config_id}")
        except Exception as e:
            logger.error(f"Error in refresh loop for dashboard {self.config_id}: {e}")
    
    async def create_embed(self):
        """Create embed from components."""
        try:
            # Build components if not cached
            if not self.components_cache:
                self.components_cache = await self.dashboard_builder.build_dashboard(self.config, self.data)
                
            return self.components_cache.get('embed')
            
        except Exception as e:
            logger.error(f"Error creating embed for dashboard {self.config_id}: {e}")
            return super().create_embed()
    
    async def create_view(self):
        """Create view from components."""
        try:
            # Build components if not cached
            if not self.components_cache:
                self.components_cache = await self.dashboard_builder.build_dashboard(self.config, self.data)
                
            return self.components_cache.get('view')
            
        except Exception as e:
            logger.error(f"Error creating view for dashboard {self.config_id}: {e}")
            return super().create_view()
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handle refresh button clicks."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Refresh data and update dashboard
            await self.refresh_data()
            await self.display_dashboard()
            
            await interaction.followup.send("Dashboard refreshed!", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error handling refresh for dashboard {self.config_id}: {e}")
            await interaction.followup.send(f"Error refreshing dashboard: {str(e)}", ephemeral=True)
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            # Cancel refresh task
            if self.refresh_task and not self.refresh_task.done():
                self.refresh_task.cancel()
                
            logger.debug(f"Cleaned up resources for dashboard {self.config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up dashboard {self.config_id}: {e}")
            return False
    
    async def display_dashboard(self) -> Optional[nextcord.Message]:
        """Display or update the dashboard message."""
        try:
            if not self.channel:
                logger.error(f"Channel not available for dashboard {self.config_id}")
                return None
                
            # Refresh components cache
            self._cached_components = await self.dashboard_builder.build_dashboard(
                self.dashboard, self.data
            )
            
            embed = self._cached_components.get('embed')
            view = self._cached_components.get('view')
            
            if not embed:
                logger.error(f"Failed to get embed for dashboard {self.config_id}")
                return None
                
            # Update existing message or create new one
            if self.message:
                try:
                    self.message = await self.message.edit(embed=embed, view=view)
                    logger.debug(f"Updated dashboard message {self.config_id}")
                except (nextcord.NotFound, nextcord.HTTPException):
                    # Message was deleted or not found, create new one
                    self.message = await self.channel.send(embed=embed, view=view)
                    logger.debug(f"Re-created dashboard message {self.config_id}")
            else:
                # Create new message
                self.message = await self.channel.send(embed=embed, view=view)
                logger.debug(f"Created new dashboard message {self.config_id}")
                
            # Update dashboard with message ID
            if self.message and self.dashboard.message_id != self.message.id:
                self.dashboard.message_id = self.message.id
                await self.dashboard_service.update_dashboard(
                    self.dashboard.id, 
                    {"message_id": self.message.id}
                )
                
            return self.message
            
        except Exception as e:
            logger.error(f"Error displaying dashboard {self.config_id}: {e}")
            return None

    async def load_components(self):
        """Load all UI components from database based on dashboard type"""
        try:
            async with self.bot.db_session() as session:
                from app.shared.infrastructure.repositories.discord.dashboard_repository_impl import DashboardRepositoryImpl
                repository = DashboardRepositoryImpl(session)
                
                # Load buttons
                buttons = await repository.get_components_by_type(
                    dashboard_type=self.config_id,
                    component_type="button"
                )
                for button in buttons:
                    self.components[f"button_{button.id}"] = self.ui_factory.create_button(
                        label=button.title,
                        custom_id=button.custom_id,
                        style=button.style,
                        emoji=button.emoji
                    )
                
                # Load embeds, views, selectors similarly
                # ...
                
            return True
        except Exception as e:
            logger.error(f"Failed to load components for {self.config_id}: {e}")
            return False
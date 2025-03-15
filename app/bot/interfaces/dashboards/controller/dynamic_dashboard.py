from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime
import json

from app.shared.logging import logger
from .base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.components.common.embeds import DashboardEmbed
from app.bot.interfaces.dashboards.components.factories.ui_component_factory import UIComponentFactory


class DynamicDashboardController(BaseDashboardController):
    """Dynamically builds dashboards from database configurations"""
    
    DASHBOARD_TYPE = "dynamic"
    
    def __init__(self, bot, dashboard_id):
        super().__init__(bot)
        self.dashboard_id = dashboard_id
        self.config = None
        self.components = {}
        self.ui_factory = UIComponentFactory()
    
    async def initialize(self):
        """Load dashboard config from database"""
        self.config = await self.service.get_dashboard_config(self.dashboard_id)
        if not self.config:
            logger.error(f"Dashboard configuration not found for ID: {self.dashboard_id}")
            return False
            
        self.title = self.config.get("title", "Dynamic Dashboard")
        self.TITLE_IDENTIFIER = self.title
        
        # Get channel from config
        channel_id = self.config.get("channel_id")
        if channel_id:
            self.channel = self.bot.get_channel(int(channel_id))
            if not self.channel:
                logger.error(f"Channel not found for dashboard {self.dashboard_id}")
                return False
        
        self.initialized = True
        return True
    
    async def create_embed(self):
        """Create embed from configuration"""
        embed_config = self.config.get("embed", {})
        
        # Create base embed
        embed = DashboardEmbed.create_dashboard_embed(
            title=embed_config.get("title", self.title),
            description=embed_config.get("description", ""),
            color=int(embed_config.get("color", "0x3498db"), 16)
        )
        
        # Add fields if defined
        for field in embed_config.get("fields", []):
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", False)
            )
            
        # Apply dynamic data processing if needed
        if "dynamic_content" in embed_config:
            await self._process_dynamic_content(embed, embed_config["dynamic_content"])
            
        # Add standard footer
        self.apply_standard_footer(embed)
            
        return embed
    
    async def _process_dynamic_content(self, embed, dynamic_config):
        """Process dynamic content for the embed"""
        if not dynamic_config:
            return
            
        content_type = dynamic_config.get("type")
        
        if content_type == "system_metrics":
            # Fetch system metrics
            metrics = await self.service.get_system_metrics()
            # Add metrics to embed
            embed.add_field(
                name="CPU Usage",
                value=f"{metrics.get('cpu_usage', 0)}%",
                inline=True
            )
            embed.add_field(
                name="Memory Usage",
                value=f"{metrics.get('memory_used', 0)}%",
                inline=True
            )
            # Add more metrics as needed
            
        elif content_type == "project_status":
            # Get projects
            projects = await self.service.get_projects()
            # Format and add to embed
            status_counts = {"Open": 0, "In Progress": 0, "Completed": 0}
            for project in projects:
                status = project.get("status", "Unknown")
                if status in status_counts:
                    status_counts[status] += 1
                    
            status_text = "\n".join([f"{status}: {count}" for status, count in status_counts.items()])
            embed.add_field(
                name="Project Status",
                value=status_text or "No projects found",
                inline=False
            )
        
        # Add more dynamic content types as needed
    
    def create_view(self):
        """Create view with components from configuration"""
        view = nextcord.ui.View(timeout=None)
        
        # Add buttons based on config
        for btn_config in self.config.get("buttons", []):
            button_type = btn_config.get("type")
            
            if button_type == "refresh":
                btn = RefreshButton(callback=self.on_refresh)
                view.add_item(btn)
            elif button_type == "custom":
                btn = BaseButton(
                    label=btn_config.get("label", "Button"),
                    style=getattr(nextcord.ButtonStyle, btn_config.get("style", "primary")),
                    custom_id=btn_config.get("custom_id", f"button_{btn_config.get('action')}"),
                    row=btn_config.get("row", 0),
                    callback=lambda i, action=btn_config.get("action"): self.handle_dynamic_action(i, action)
                )
                view.add_item(btn)
                
        # Add selects if configured
        for select_config in self.config.get("selects", []):
            select_type = select_config.get("type")
            
            if select_type == "string":
                select = StringSelect(
                    custom_id=select_config.get("custom_id", "string_select"),
                    placeholder=select_config.get("placeholder", "Select an option"),
                    options=[
                        nextcord.SelectOption(
                            label=option.get("label", "Option"),
                            value=option.get("value", option.get("label", "Option")),
                            description=option.get("description", ""),
                            emoji=option.get("emoji")
                        ) for option in select_config.get("options", [])
                    ],
                    callback=lambda i: self.handle_select(i)
                )
                view.add_item(select)
                
        return view
    
    async def handle_dynamic_action(self, interaction, action):
        """Handle actions defined in the configuration"""
        # First check rate limiting
        if not await self.check_rate_limit(interaction, f"action_{action}"):
            return

        try:
            # Look up the action handler in the config
            action_handlers = self.config.get("action_handlers", {})
            
            if action in action_handlers:
                handler_config = action_handlers[action]
                await self._execute_action_handler(interaction, handler_config)
            else:
                # Default implementations for common actions
                if action == "refresh":
                    await self.on_refresh(interaction)
                elif action == "show_details":
                    await self.show_details(interaction)
                else:
                    await interaction.response.send_message(f"Action '{action}' not implemented", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in dynamic action handler: {e}")
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    async def _execute_action_handler(self, interaction, handler_config):
        """Execute a configured action handler"""
        handler_type = handler_config.get("type")
        
        if handler_type == "send_message":
            await interaction.response.send_message(
                handler_config.get("message", "Action executed"),
                ephemeral=handler_config.get("ephemeral", True)
            )
        elif handler_type == "show_modal":
            # Create a modal from config
            modal_config = handler_config.get("modal", {})
            modal = self._create_dynamic_modal(modal_config)
            await interaction.response.send_modal(modal)
        elif handler_type == "api_call":
            # Call an API and show results
            await interaction.response.defer(ephemeral=True)
            # API call logic here
            await interaction.followup.send("API call completed", ephemeral=True)
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the refresh button"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "refresh"):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Fetch and refresh data
            self.config = await self.service.get_dashboard_config(self.dashboard_id)
            
            # Update the dashboard message with new data
            await self.display_dashboard()
            
            await interaction.followup.send(
                "Dashboard updated with latest data!", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {str(e)}")
            error_embed = self.create_error_embed(
                error_message=str(e),
                title="❌ Refresh Error",
                error_code="DYNAMIC-REFRESH-ERR"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
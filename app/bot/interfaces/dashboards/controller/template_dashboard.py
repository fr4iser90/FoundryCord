from typing import Dict, Any, Optional
import nextcord
from datetime import datetime

from app.shared.logging import logger
from app.bot.infrastructure.config.channel_config import ChannelConfig
from .base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.components.common.embeds import DashboardEmbed


class TemplateDashboardController(BaseDashboardController):
    """UI class for displaying a template dashboard"""
    
    DASHBOARD_TYPE = "template"
    TITLE_IDENTIFIER = "Template Dashboard"
    
    def __init__(self, bot):
        super().__init__(bot)
        self.service = None
        self.last_metrics = {}  # Cached data for the dashboard
    
    def set_service(self, service):
        """Sets the service for this UI component"""
        self.service = service
        return self
    
    async def initialize(self):
        """Initialize the template dashboard UI"""
        logger.info("Template Dashboard UI initialized")
        return await super().initialize(channel_config_key='template')  # Update with your channel config key
    
    async def create_embed(self) -> nextcord.Embed:
        """Creates the dashboard embed with data"""
        if not self.service:
            logger.error("Template service not available")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description="Template service not available",
                color=0xff0000
            )
        
        try:
            # Fetch data from the service
            data = await self.service.get_template_data()
            
            # Store the data for button handlers to use
            self.last_metrics = data
            
            # Create the main embed
            embed = nextcord.Embed(
                title=f"📊 {self.TITLE_IDENTIFIER}",
                description="Description of your dashboard purpose",
                color=0x3498db  # Blue color
            )
            
            # Add data to the embed
            embed.add_field(
                name="Field 1",
                value="Content for field 1 from your data",
                inline=False
            )
            
            embed.add_field(
                name="Field 2",
                value="Content for field 2 from your data",
                inline=True
            )
            
            embed.add_field(
                name="Field 3",
                value="Content for field 3 from your data",
                inline=True
            )
            
            # Add standard footer
            DashboardEmbed.add_standard_footer(embed)
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating template embed: {str(e)}")
            return self.create_error_embed(str(e))
    
    def create_view(self) -> nextcord.ui.View:
        """Create a view with dashboard buttons"""
        view = nextcord.ui.View(timeout=None)
        
        # Refresh button (included by default in BaseDashboardController)
        # You can access it with self.on_refresh
        
        # Add your custom buttons
        details_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="View Details",
            emoji="📋",
            custom_id="view_details"
        )
        details_button.callback = self.on_view_details
        
        action_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.success,
            label="Action",
            emoji="✅",
            custom_id="perform_action"
        )
        action_button.callback = self.on_perform_action
        
        view.add_item(details_button)
        view.add_item(action_button)
        
        return view
    
    async def register_callbacks(self, view):
        """Register button callbacks for the dashboard"""
        # Find buttons by their custom_id and assign callbacks
        for item in view.children:
            if hasattr(item, 'custom_id'):
                if item.custom_id == "view_details":
                    item.callback = self.on_view_details
                elif item.custom_id == "perform_action":
                    item.callback = self.on_perform_action
        
        # Also register the refresh button from parent
        view.set_callback("refresh", self.on_refresh)
    
    async def on_view_details(self, interaction: nextcord.Interaction):
        """Handler for the view details button"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "view_details"):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get data for details view
            details = await self.service.get_detail_data()
            
            # Create an embed or message to show the details
            details_text = "Here are the details:\n"
            for key, value in details.items():
                details_text += f"• **{key}**: {value}\n"
            
            await interaction.followup.send(details_text, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying details: {e}")
            error_embed = self.create_error_embed(
                error_message=str(e),
                title="❌ Details Error",
                error_code="TEMPLATE-DETAIL-ERR"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    async def on_perform_action(self, interaction: nextcord.Interaction):
        """Handler for the action button"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "perform_action"):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Perform some action via the service
            result = await self.service.perform_action()
            
            # Create response based on result
            if result:
                await interaction.followup.send("✅ Action completed successfully!", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Action could not be completed.", ephemeral=True)
            
            # Update the dashboard after action
            await self.display_dashboard()
            
        except Exception as e:
            logger.error(f"Error performing action: {e}")
            error_embed = self.create_error_embed(
                error_message=str(e),
                title="❌ Action Error",
                error_code="TEMPLATE-ACTION-ERR"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the refresh button"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "refresh"):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get fresh data
            data = await self.service.get_template_data()
            self.last_metrics = data
            
            # Update the dashboard with fresh data
            await self.display_dashboard()
            
            await interaction.followup.send("Dashboard has been refreshed!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            await interaction.followup.send(f"Error refreshing: {str(e)}", ephemeral=True) 
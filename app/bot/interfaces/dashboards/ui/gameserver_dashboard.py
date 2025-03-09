# app/bot/interfaces/dashboards/ui/gameserver_dashboard.py
from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.channels.gameservers.views import GameServerView
from domain.gameservers.models.gameserver_metrics import GameServersMetrics
from interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder

class GameServerDashboardUI(BaseDashboardUI):
    """UI class for displaying the game server dashboard"""
    
    DASHBOARD_TYPE = "gameservers"
    TITLE_IDENTIFIER = "Game Servers Status"
    
    async def initialize(self):
        """Initialize the game server dashboard UI"""
        return await super().initialize(channel_config_key='gameservers')
    
    async def create_embed(self) -> nextcord.Embed:
        """Creates game server dashboard embed with server data"""
        if not self.service:
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description="Game Server service not available",
                color=0xff0000
            )
        
        try:
            # Get raw data from service
            data = await self.service.get_game_servers_status()
            
            # Transform data using domain model
            game_metrics = GameServersMetrics.from_raw_data(data)
            
            # Convert to dictionary for the view
            metrics = game_metrics.to_dict()
            
            # Store metrics for button handlers to use
            self.last_metrics = metrics
            self.game_metrics = game_metrics  # Store the domain object too
            
            # Create view and embed
            gameserver_view = GameServerView(metrics)
            embed = gameserver_view.create_embed()
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating game server embed: {e}")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description=f"Error creating dashboard: {str(e)}",
                color=0xff0000
            )
    
    async def update_dashboard(self, interaction: Optional[nextcord.Interaction] = None):
        """Updates the game server dashboard with fresh data"""
        try:
            # Force cleanup before updating
            await self.cleanup_old_dashboards(keep_count=1)
            
            # Get fresh data from service
            data = await self.service.get_game_servers_status()
            
            # Transform data using domain model
            game_metrics = GameServersMetrics.from_raw_data(data)
            
            # Convert to dictionary for the view
            metrics = game_metrics.to_dict()
            
            # Store metrics for button handlers to use
            self.last_metrics = metrics
            self.game_metrics = game_metrics
            
            # Create view and embed
            gameserver_view = GameServerView(metrics)
            embed = gameserver_view.create_embed()
            view = gameserver_view.create()
            
            # Register button callbacks
            await self.register_callbacks(view)
            
            # Update the dashboard
            if interaction:
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                self.message = await self.channel.send(embed=embed, view=view) if not self.message else await self.message.edit(embed=embed, view=view)
            
            return embed
            
        except Exception as e:
            logger.error(f"Error updating game server dashboard: {e}")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description=f"Error updating dashboard: {str(e)}",
                color=0xff0000
            )
    
    async def on_server_details(self, interaction: nextcord.Interaction):
        """Show detailed server information for a specific server"""
        await interaction.response.defer()
        
        try:
            # Create a selection menu with all available servers
            servers = self.last_metrics['servers'] if hasattr(self, 'last_metrics') else {}
            
            if not servers:
                await interaction.followup.send("No game servers found", ephemeral=True)
                return
                
            # Create select menu with server options
            options = []
            for name, server_data in servers.items():
                status = "🟢 Online" if server_data['online'] else "🔴 Offline"
                options.append(
                    nextcord.SelectOption(
                        label=name, 
                        description=status,
                        emoji="🎮"
                    )
                )
            
            # Create view with select menu
            view = nextcord.ui.View(timeout=60)
            select = nextcord.ui.Select(
                placeholder="Choose a server",
                options=options
            )
            
            async def select_callback(select_interaction):
                server_name = select_interaction.data["values"][0]
                server_details = await self.service.get_server_details(server_name)
                
                server_table = UnicodeTableBuilder(f"{server_name} Details", width=50)
                server_table.add_header_row("Property", "Value")
                server_table.add_row("Status", "🟢 Online" if servers[server_name]['online'] else "🔴 Offline")
                server_table.add_row("Version", server_details.get('version', 'Unknown'))
                server_table.add_row("Uptime", server_details.get('uptime', 'Unknown'))
                server_table.add_row("Players", f"{server_details.get('player_count', 0)}/{server_details.get('max_players', 0)}")
                server_table.add_row("Ports", ", ".join(map(str, server_details.get('ports', []))))
                server_table.add_row("CPU Usage", server_details.get('cpu_usage', 'Unknown'))
                server_table.add_row("Memory Usage", server_details.get('memory_usage', 'Unknown'))
                server_table.add_row("World Size", server_details.get('world_size', 'Unknown'))
                
                await select_interaction.response.edit_message(content=server_table.build(), view=None)
            
            select.callback = select_callback
            view.add_item(select)
            
            await interaction.followup.send("Select a server for details:", view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying server details: {e}")
            await interaction.followup.send(f"Error displaying server details: {str(e)}", ephemeral=True)
    
    async def on_player_list(self, interaction: nextcord.Interaction):
        """Show player list for a server"""
        await interaction.response.defer()
        
        try:
            # Create a selection menu with all available servers
            servers = self.last_metrics['servers'] if hasattr(self, 'last_metrics') else {}
            
            if not servers:
                await interaction.followup.send("No game servers found", ephemeral=True)
                return
                
            # Only show online servers
            online_servers = {name: data for name, data in servers.items() if data['online']}
            
            if not online_servers:
                await interaction.followup.send("No online game servers found", ephemeral=True)
                return
            
            # Create select menu with server options
            options = []
            for name, server_data in online_servers.items():
                options.append(
                    nextcord.SelectOption(
                        label=name, 
                        description=f"Players: {server_data.get('player_count', 0)}",
                        emoji="👥"
                    )
                )
            
            # Create view with select menu
            view = nextcord.ui.View(timeout=60)
            select = nextcord.ui.Select(
                placeholder="Choose a server",
                options=options
            )
            
            async def select_callback(select_interaction):
                server_name = select_interaction.data["values"][0]
                server_details = await self.service.get_server_details(server_name)
                
                players = server_details.get('players', [])
                
                if not players:
                    await select_interaction.response.edit_message(content=f"No players online on {server_name}", view=None)
                    return
                
                player_table = UnicodeTableBuilder(f"Players on {server_name}", width=50)
                player_table.add_header_row("Player", "Joined", "Playtime")
                
                for player in players:
                    # In a real implementation, you'd have more player data
                    player_table.add_row(player, "Today", "2h 30m")
                
                await select_interaction.response.edit_message(content=player_table.build(), view=None)
            
            select.callback = select_callback
            view.add_item(select)
            
            await interaction.followup.send("Select a server to view players:", view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying player list: {e}")
            await interaction.followup.send(f"Error displaying player list: {str(e)}", ephemeral=True)
    
    async def on_server_logs(self, interaction: nextcord.Interaction):
        """Show server logs"""
        await interaction.response.defer()
        
        try:
            # Create a selection menu with all available servers
            servers = self.last_metrics['servers'] if hasattr(self, 'last_metrics') else {}
            
            if not servers:
                await interaction.followup.send("No game servers found", ephemeral=True)
                return
            
            # Create select menu with server options
            options = []
            for name, server_data in servers.items():
                status = "🟢 Online" if server_data['online'] else "🔴 Offline"
                options.append(
                    nextcord.SelectOption(
                        label=name, 
                        description=status,
                        emoji="📜"
                    )
                )
            
            # Create view with select menu
            view = nextcord.ui.View(timeout=60)
            select = nextcord.ui.Select(
                placeholder="Choose a server",
                options=options
            )
            
            async def select_callback(select_interaction):
                server_name = select_interaction.data["values"][0]
                logs = await self.service.get_server_logs(server_name)
                
                if not logs:
                    await select_interaction.response.edit_message(content=f"No logs available for {server_name}", view=None)
                    return
                
                logs_formatted = "```\n" + "\n".join(logs) + "\n```"
                await select_interaction.response.edit_message(content=f"**Latest logs for {server_name}**\n{logs_formatted}", view=None)
            
            select.callback = select_callback
            view.add_item(select)
            
            await interaction.followup.send("Select a server to view logs:", view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying server logs: {e}")
            await interaction.followup.send(f"Error displaying server logs: {str(e)}", ephemeral=True)
    
    async def register_callbacks(self, view):
        """Register callbacks for the view's buttons"""
        view.set_callback("refresh", self.on_refresh)
        view.set_callback("server_details", self.on_server_details)
        view.set_callback("player_list", self.on_player_list)
        view.set_callback("server_logs", self.on_server_logs)
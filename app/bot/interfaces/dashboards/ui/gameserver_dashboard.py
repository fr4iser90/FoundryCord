# app/bot/interfaces/dashboards/ui/gameserver_dashboard.py
from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.channels.gameservers.views import GameServerView
from interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder
from domain.gameservers.collectors.minecraft.minecraft_server_collector import MinecraftServerFetcher
from domain.gameservers.models.gameserver_metrics import GameServersMetrics


class GameServerDashboardUI(BaseDashboardUI):
    """UI class for displaying the game server dashboard"""
    
    DASHBOARD_TYPE = "gameservers"
    TITLE_IDENTIFIER = "Game Servers Status"
    
    def __init__(self, bot):
        super().__init__(bot)
        self.minecraft_collector = MinecraftServerFetcher()
        self.metrics = GameServersMetrics()  # Domain model
    
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
    
    async def display_dashboard(self) -> nextcord.Message:
        """Display the game server dashboard"""
        try:
            embed = await self.create_embed()
            
            # Create the view with buttons
            view = GameServerView(self.last_metrics).create()
            
            # Register callbacks for the buttons
            await self.register_callbacks(view)
            
            # Send or update the message
            if self.message:
                await self.message.edit(embed=embed, view=view)
            else:
                self.message = await self.channel.send(embed=embed, view=view)
            
            return self.message
        except Exception as e:
            logger.error(f"Error displaying game server dashboard: {e}")
            raise
    
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
    
    async def on_connection_details(self, interaction: nextcord.Interaction):
        """Show detailed connection information"""
        await interaction.response.defer()
        
        try:
            # Get domain and IP information
            public_ip = self.last_metrics.get('public_ip', 'Unknown')
            domain = self.last_metrics.get('domain', 'Unknown')
            ip_match = self.last_metrics.get('ip_match', None)
            
            # Create a table with connection details
            conn_table = UnicodeTableBuilder("Game Server Connection Details", width=50)
            conn_table.add_header_row("Property", "Value")
            conn_table.add_row("Domain", domain)
            conn_table.add_row("Public IP", public_ip)
            
            # Check if domain resolves to public IP
            status = "🟢 Correct" if ip_match else "🔴 Mismatch" if ip_match is not None else "⚠️ Unknown"
            conn_table.add_row("DNS Status", status)
            
            # Add connection instructions
            servers = self.last_metrics.get('servers', {})
            online_servers = {name: data for name, data in servers.items() if data.get('online', False)}
            
            if online_servers:
                conn_table.add_header_row("Server", "Connection Address")
                for name, data in online_servers.items():
                    ports = data.get('ports', [])
                    if ports:
                        port_str = ports[0]  # Use first port for connection
                        conn_table.add_row(name, f"{domain}:{port_str}")
            
            await interaction.followup.send(conn_table.build(), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying connection details: {e}")
            await interaction.followup.send(f"Error displaying connection details: {str(e)}", ephemeral=True)
    
    async def register_callbacks(self, view):
        """Register callbacks for the view's buttons"""
        view.set_callback("refresh", self.on_refresh)
        view.set_callback("server_details", self.on_server_details)
        view.set_callback("player_list", self.on_player_list)
        view.set_callback("server_logs", self.on_server_logs)
        view.set_callback("connection_details", self.on_connection_details)

    async def refresh_data(self):
        """Fetch all game server data and update metrics"""
        # Get base metrics from your existing source
        base_data = await self.service.get_game_servers_status()
        self.metrics = GameServersMetrics.from_raw_data(base_data)
        
        # Fetch and integrate Minecraft-specific data
        domain = self.metrics.domain or "fr4iser.com"
        minecraft_servers = [(domain, 25570)]  # Use correct port 25570
        
        try:
            logger.debug(f"🎮 GameServerDashboardUI: Fetching Minecraft data for {minecraft_servers}")
            minecraft_data = await MinecraftServerFetcher.fetch_multiple_servers(minecraft_servers)
            
            # Add detailed logging
            logger.debug(f"==== RAW MINECRAFT API RESPONSE ====")
            for server_key, server_data in minecraft_data.items():
                logger.debug(f"Server {server_key}:")
                logger.debug(f"  Online: {server_data.get('online')}")
                logger.debug(f"  Player count: {server_data.get('player_count')}")
                logger.debug(f"  Max players: {server_data.get('max_players')}")
                logger.debug(f"  Player list: {server_data.get('players', [])}")
            
            # Update metrics with Minecraft data
            self.metrics.update_with_minecraft_data(minecraft_data)
            
            # Log the processed data
            logger.debug("==== PROCESSED MINECRAFT DATA ====")
            for name, server in self.metrics.servers.items():
                if "minecraft" in name.lower():
                    logger.debug(f"Server {name}:")
                    logger.debug(f"  Online: {server.online}")
                    logger.debug(f"  Player count: {server.player_count}")
                    logger.debug(f"  Max players: {server.max_players}")
                    logger.debug(f"  Player list: {server.players}")
            
            # Update last_metrics for UI to use
            self.last_metrics = self.metrics.to_dict()
            
            logger.info(f"Updated metrics with Minecraft data for {len(minecraft_data)} servers")
        except Exception as e:
            logger.error(f"Failed to fetch Minecraft data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Create a view with the updated metrics
        view = GameServerView(self.metrics.to_dict())
        view.create()  # Make sure to call create to set up the buttons
        return view
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the refresh button"""
        await interaction.response.defer(ephemeral=True)
        
        # Fetch and refresh data
        await self.create_embed()
        await self.refresh_data()
        
        # Critical: Update the dashboard message with new data
        await self.display_dashboard()
        
        await interaction.followup.send(
            "Game Server Dashboard updated with latest data!", 
            ephemeral=True
        )
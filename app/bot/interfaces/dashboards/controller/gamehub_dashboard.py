# app/bot/interfaces/dashboards/ui/gamehub_dashboard.py
from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from .base_dashboard import BaseDashboardController
from interfaces.dashboards.components.channels.gamehub.views import GameHubView
from interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder
from infrastructure.monitoring.collectors.game_servers.minecraft_server_collector_impl import MinecraftServerFetcher
from domain.gameservers.models.gameserver_metrics import GameServersMetrics

class GameHubDashboardController(BaseDashboardController):
    """UI class for displaying the Game Hub dashboard"""
    
    DASHBOARD_TYPE = "gamehub"
    TITLE_IDENTIFIER = "Game Hub"
    
    def __init__(self, bot):
        super().__init__(bot)
        self.minecraft_collector = MinecraftServerFetcher()
        self.metrics = GameServersMetrics()  # Domain model
        self.last_metrics = {}  # Initialize empty metrics
    
    async def initialize(self):
        """Initialize the Game Hub dashboard UI"""
        return await super().initialize(channel_config_key='gamehub')
    
    async def create_embed(self) -> nextcord.Embed:
        """Create the game hub embed"""
        embed = nextcord.Embed(
            title="🎮 Game Servers Status",
            description="Current status of game servers",
            color=0x3498db
        )
        
        # Prüfe, ob wir Daten haben
        if hasattr(self, 'last_metrics') and self.last_metrics:
            # Hole die Server-Daten aus dem richtigen Schlüssel
            servers = self.last_metrics.get('servers', {})
            
            # Füge alle Game-Server hinzu
            for name, status in servers.items():
                if '🎮' in name:
                    embed.add_field(
                        name=name,
                        value=status,
                        inline=True
                    )
        else:
            embed.add_field(
                name="Status",
                value="⚠️ Unable to fetch server status",
                inline=False
            )
            
        return embed
    
    async def update_metrics(self):
        """Update game server metrics"""
        try:
            logger.debug("Collecting game server data for game server dashboard")
            
            # Hole die Rohdaten
            raw_data = await self.service.get_game_servers_status_dict()
            
            # SPEICHERE DIE ROHDATEN DIREKT (OHNE KONVERSION)
            self.last_metrics = raw_data
            
            # Verwende die Daten direkt in create_embed
            logger.debug(f"Saved raw server data: {self.last_metrics}")
            
        except Exception as e:
            logger.error(f"Error updating game hub metrics: {e}")
            self.last_metrics = {'servers': {}}  # Leeres Dict mit servers-Key
    
    async def display_dashboard(self) -> nextcord.Message:
        """Display the Game Hub dashboard"""
        try:
            if not self.channel:
                logger.error("No channel configured for game hub dashboard")
                return None
                
            # Clean up old dashboards first
            await self.cleanup_old_dashboards(keep_count=1)
            
            # Get fresh metrics before display
            await self.update_metrics()
            
            # Create embed and view
            embed = await self.create_embed()
            view = GameHubView(self.last_metrics).create()
            
            # Register callbacks
            await self.register_callbacks(view)
            
            # If we have an existing message, update it
            if self.message and hasattr(self.message, 'edit'):
                try:
                    await self.message.edit(embed=embed, view=view)
                    logger.info(f"Updated existing game hub dashboard in {self.channel.name}")
                    return self.message
                except Exception as e:
                    logger.warning(f"Couldn't update existing message: {e}, creating new")
            
            # Otherwise send a new message
            try:
                message = await self.channel.send(embed=embed, view=view)
                self.message = message
                
                # Track in dashboard manager
                await self.bot.dashboard_manager.track_message(
                    dashboard_type=self.DASHBOARD_TYPE,
                    message_id=message.id,
                    channel_id=self.channel.id
                )
                
                logger.info(f"Game hub dashboard displayed in channel {self.channel.name}")
                return message
            except Exception as e:
                logger.error(f"Error sending game hub dashboard: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error displaying game hub dashboard: {e}")
            raise
    
    async def on_server_details(self, interaction: nextcord.Interaction):
        """Show detailed server information for a specific server"""
        await interaction.response.defer()
        
        try:
            # Create a selection menu with all available servers
            servers = self.last_metrics.get('servers', {}) if hasattr(self, 'last_metrics') else {}
            
            if not servers:
                await interaction.followup.send("No game servers found", ephemeral=True)
                return
                
            # Create select menu with server options
            options = []
            for name, server_data in servers.items():
                # Check if the value is a string (new format) or dict (old format)
                if isinstance(server_data, str):
                    status = "🟢 Online" if "Online" in server_data or "✅" in server_data else "🔴 Offline"
                else:
                    # Original behavior for dict format
                    status = "🟢 Online" if server_data.get('online', False) else "🔴 Offline"
                    
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
                
                # Get status from server data
                server_data = servers.get(server_name, "")
                if isinstance(server_data, str):
                    status = "🟢 Online" if "Online" in server_data or "✅" in server_data else "🔴 Offline"
                else:
                    status = "🟢 Online" if server_data.get('online', False) else "🔴 Offline"
                    
                server_table.add_row("Status", status)
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
            servers = self.last_metrics.get('servers', {}) if hasattr(self, 'last_metrics') else {}
            
            if not servers:
                await interaction.followup.send("No game servers found", ephemeral=True)
                return
                
            # Only show online servers
            online_servers = {}
            for name, data in servers.items():
                if isinstance(data, str):
                    if "Online" in data or "✅" in data:
                        online_servers[name] = {'player_count': 0}  # Default count
                elif isinstance(data, dict) and data.get('online', False):
                    online_servers[name] = data
            
            if not online_servers:
                await interaction.followup.send("No online game servers found", ephemeral=True)
                return
            
            # Create select menu with server options
            options = []
            for name, server_data in online_servers.items():
                player_count = server_data.get('player_count', 0) if isinstance(server_data, dict) else 0
                options.append(
                    nextcord.SelectOption(
                        label=name, 
                        description=f"Players: {player_count}",
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
            conn_table = UnicodeTableBuilder("Game Hub Connection Details", width=50)
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
        """Fetch all Game Hub data and update metrics"""
        try:
            # Get dictionary data
            base_data = await self.service.get_game_servers_status_dict()
            
            # Format the data for GameServersMetrics
            formatted_data = {
                'system': {},
                'services': {
                    'services': {}
                }
            }
            
            # Format the game servers data properly
            for server_name, server_info in base_data.items():
                # Create game server entry with proper format
                status_text = "✅ Online" if server_info.get('online', False) else "❌ Offline"
                if 'ports' in server_info:
                    status_text += f" Port(s): {', '.join(map(str, server_info['ports']))}"
                    
                # Add to formatted data
                formatted_data['services']['services'][f"🎮 {server_name}"] = status_text
            
            # Create metrics object
            self.metrics = GameServersMetrics.from_raw_data(formatted_data)
            
            # Store raw data for UI display
            self.last_metrics = base_data
            
            # Fetch and integrate Minecraft-specific data
            domain = self.metrics.domain or "fr4iser.com"
            minecraft_servers = [(domain, 25570)]  # Use correct port 25570
            
            try:
                logger.debug(f"🎮 GameHubDashboardController: Fetching Minecraft data for {minecraft_servers}")
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
            view = GameHubView(self.metrics.to_dict() if hasattr(self.metrics, 'to_dict') else {})
            view.create()
            return view
        except Exception as e:
            logger.error(f"Failed to refresh data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Initialize empty data structures
            self.last_metrics = {}
            self.metrics = GameServersMetrics()
        
        # Create a view with the metrics
        view = GameHubView(self.metrics.to_dict() if hasattr(self.metrics, 'to_dict') else {})
        view.create()
        return view
    
    async def create_view(self) -> nextcord.ui.View:
        """Create the dashboard view with buttons and components"""
        try:
            # Make sure metrics is properly formatted as a dictionary
            metrics_data = self.metrics.to_dict() if hasattr(self.metrics, 'to_dict') else {}
            
            # Ensure metrics_data is a dictionary, not a string
            if isinstance(metrics_data, str):
                logger.warning(f"Expected dictionary for metrics, got string: {metrics_data}")
                metrics_data = {"error": metrics_data}
                
            # Create a view with the metrics
            view = GameHubView(metrics_data)
            view.create()
            return view
        except Exception as e:
            logger.error(f"Failed to create view: {str(e)}")
            # Return empty view as fallback
            empty_view = GameHubView({})
            empty_view.create()
            return empty_view
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the refresh button"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Fetch and refresh data
            await self.refresh_data()
            
            # Critical: Update the dashboard message with new data
            await self.display_dashboard()
            
            await interaction.followup.send(
                "Game Hub Dashboard updated with latest data!", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {str(e)}")
            await interaction.followup.send(
                f"An error occurred while refreshing: {str(e)}", 
                ephemeral=True
            )
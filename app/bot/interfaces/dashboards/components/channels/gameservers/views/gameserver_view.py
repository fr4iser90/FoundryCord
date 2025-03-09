# app/bot/interfaces/dashboards/components/channels/gameservers/views/gameserver_view.py
import nextcord
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from infrastructure.logging import logger
from interfaces.dashboards.components.common.views import BaseView
from interfaces.dashboards.components.common.buttons import RefreshButton
from interfaces.dashboards.components.channels.gameservers.buttons import GameServerButton

class GameServerView(BaseView):
    """View for game server dashboard with styled metrics and sections"""
    
    def __init__(
        self,
        metrics: Dict[str, Any] = None,
        timeout: Optional[int] = None
    ):
        super().__init__(timeout=timeout)
        self.metrics = metrics or {}
    
    def create_embed(self) -> nextcord.Embed:
        """Creates a beautifully formatted game server dashboard embed"""
        embed = nextcord.Embed(
            title="🎮 Game Server Dashboard",
            description="Current status of all game servers",
            color=0x7289da,  # Discord blurple
            timestamp=datetime.now()
        )
        
        # Get server data
        servers = self.metrics.get('servers', {})
        online_count = self.metrics.get('online_servers', 0)
        total_count = self.metrics.get('total_servers', 0)
        player_count = self.metrics.get('total_players', 0)
        
        # Connection information
        public_ip = self.metrics.get('public_ip', 'Unknown')
        domain = self.metrics.get('domain', 'Unknown')
        ip_match = self.metrics.get('ip_match', None)
        
        # Add connection information with indicator when there's a mismatch
        if ip_match is not None:
            connection_warning = "" if ip_match else "⚠️ Domain and IP don't match! Check DNS settings."
            connection_color = 0x2ecc71 if ip_match else 0xf1c40f  # Green or amber
            connection_info = (
                f"**Connect via:** {domain}\n"
                f"**Public IP:** {public_ip}\n"
                f"{connection_warning}"
            )
            embed.add_field(name="🔌 Connection", value=connection_info, inline=False)
        
        # Summary field
        summary = (
            f"**Servers:** {online_count}/{total_count} online\n"
            f"**Players:** {player_count} across all servers\n"
            f"**Last Updated:** {self.metrics.get('timestamp', 'Unknown')}"
        )
        embed.add_field(name="📊 Overview", value=summary, inline=False)
        
        # Group servers by game type
        game_types = {
            "Minecraft": [],
            "Factorio": [],
            "Valheim": [],
            "CS2": [],
            "Palworld": [],
            "Satisfactory": [],
            "Other": []
        }
        
        for name, data in servers.items():
            found = False
            for game_type in game_types.keys():
                if game_type.lower() in name.lower():
                    game_types[game_type].append((name, data))
                    found = True
                    break
            if not found:
                game_types["Other"].append((name, data))
        
        # Add fields for each game type with servers
        for game_type, server_list in game_types.items():
            if not server_list:
                continue
                
            field_value = ""
            for name, data in server_list:
                status_emoji = "🟢" if data.get('online', False) else "🔴"
                ports = ', '.join(map(str, data.get('ports', []))) if data.get('ports') else 'N/A'
                player_info = f"{data.get('player_count', 0)}/{data.get('max_players', 0)}" if data.get('online', False) else "-"
                
                field_value += f"{status_emoji} **{name}**\n"
                field_value += f"└ Players: {player_info} | Ports: {ports}\n"
            
            embed.add_field(name=f"{game_type} Servers", value=field_value, inline=True)
        
        # Footer with instructions
        embed.set_footer(text="Use the buttons below for more details | Last updated at " + 
                              datetime.now().strftime("%H:%M:%S"))
        
        return embed
    
    def create(self):
        """Creates a complete view with all necessary buttons"""
        
        # Refresh button
        refresh_button = RefreshButton(
            callback=lambda i: self._handle_callback(i, "refresh"),
            label="Aktualisieren"
        )
        self.add_item(refresh_button)
        
        # Server details button
        details_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Server Details",
            emoji="📋",
            custom_id="server_details",
            row=0
        )
        details_button.callback = lambda i: self._handle_callback(i, "server_details")
        self.add_item(details_button)
        
        # Player list button
        player_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Player List",
            emoji="👥",
            custom_id="player_list",
            row=0
        )
        player_button.callback = lambda i: self._handle_callback(i, "player_list")
        self.add_item(player_button)
        
        # Server logs button
        logs_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Server Logs",
            emoji="📜",
            custom_id="server_logs",
            row=1
        )
        logs_button.callback = lambda i: self._handle_callback(i, "server_logs")
        self.add_item(logs_button)
        
        # Connection info button
        connection_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Connection Info",
            emoji="🔌",
            custom_id="connection_details",
            row=1
        )
        connection_button.callback = lambda i: self._handle_callback(i, "connection_details")
        self.add_item(connection_button)
        
        return self
    
    async def _handle_callback(self, interaction: nextcord.Interaction, action: str):
        """Handle button interactions with proper async/await pattern"""
        try:
            # First, defer the response to prevent interaction timeouts
            await interaction.response.defer(ephemeral=True)
            
            if action == "refresh":
                # Let the dashboard handle refreshing, just send confirmation
                await interaction.followup.send("Refreshing game server data...", ephemeral=True)
                
            elif action == "server_details":
                # Display server details in a formatted message
                servers = self.metrics.get('servers', {})
                if not servers:
                    await interaction.followup.send("No server details available.", ephemeral=True)
                    return
                
                details = "**📊 Game Server Details**\n\n"
                for name, data in servers.items():
                    status = "🟢 Online" if data.get('online', False) else "🔴 Offline"
                    version = data.get('version', 'Unknown')
                    ports = ', '.join(map(str, data.get('ports', []))) if data.get('ports') else 'N/A'
                    
                    details += f"**{name}**\n"
                    details += f"Status: {status}\n"
                    details += f"Version: {version}\n"
                    details += f"Ports: {ports}\n\n"
                
                await interaction.followup.send(details, ephemeral=True)
                
            elif action == "player_list":
                # Display list of players on each server
                servers = self.metrics.get('servers', {})
                
                # Start building the response
                players_info = "**👥 Current Players**\n\n"
                total_players = 0
                players_found = False
                
                for name, data in servers.items():
                    online = data.get('online', False)
                    player_count = data.get('player_count', 0)
                    max_players = data.get('max_players', 0)
                    player_list = data.get('players', [])
                    
                    logger.debug(f"Processing server {name}:")
                    logger.debug(f"  Online: {online}")
                    logger.debug(f"  Player count: {player_count}")
                    logger.debug(f"  Player list: {player_list}")
                    
                    # Add server even if offline
                    players_info += f"**{name}** ({player_count}/{max_players})\n"
                    
                    if online and player_list and len(player_list) > 0:
                        players_info += "Players: " + ", ".join(player_list) + "\n\n"
                        players_found = True
                    else:
                        players_info += "No players online\n\n"
                    
                    if online:
                        total_players += player_count
                
                if total_players == 0:
                    players_info += "No players online on any server."
                
                # Always do a direct API check to ensure we have the latest data
                try:
                    from domain.gameservers.collectors.minecraft.minecraft_server_collector import MinecraftServerFetcher
                    domain = self.metrics.get('domain', 'fr4iser.com') 
                    
                    players_info += "\n\n**Direct API Check:**\n"
                    minecraft_api_data = await MinecraftServerFetcher.fetch_server_data(domain, 25570)
                    
                    mc_online = minecraft_api_data.get('online', False)
                    mc_players = minecraft_api_data.get('player_count', 0)
                    mc_max = minecraft_api_data.get('max_players', 0)
                    mc_list = minecraft_api_data.get('players', [])
                    
                    players_info += f"Minecraft: {mc_players}/{mc_max} players"
                    if mc_list:
                        players_info += f"\nPlayers: {', '.join(mc_list)}"
                except Exception as e:
                    players_info += f"\n\nAPI check error: {str(e)}"
                
                await interaction.followup.send(players_info, ephemeral=True)
                
            elif action == "server_logs":
                # Display recent logs (placeholder implementation)
                await interaction.followup.send(
                    "Server logs feature is not yet implemented. Check back later!",
                    ephemeral=True
                )
                
            elif action == "connection_details":
                # Display connection details
                public_ip = self.metrics.get('public_ip', 'Unknown')
                domain = self.metrics.get('domain', 'Unknown')
                ip_match = self.metrics.get('ip_match', None)
                
                connection_info = "**🔌 Connection Details**\n\n"
                connection_info += f"**Domain:** {domain}\n"
                connection_info += f"**Public IP:** {public_ip}\n"
                
                if ip_match is not None:
                    match_status = "✅ Domain and IP match correctly" if ip_match else "⚠️ Domain and IP don't match! Check DNS settings."
                    connection_info += f"**DNS Check:** {match_status}\n"
                    
                connection_info += "\n**Connection Instructions:**\n"
                connection_info += "1. Use the domain to connect to any game server\n"
                connection_info += "2. Make sure to use the correct port for each server\n"
                
                await interaction.followup.send(connection_info, ephemeral=True)
                
            else:
                await interaction.followup.send(f"Action '{action}' not implemented yet.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error in button callback handler: {str(e)}")
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
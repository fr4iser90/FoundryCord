# app/bot/interfaces/dashboards/components/channels/gameservers/views/gameserver_view.py
import nextcord
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from infrastructure.logging import logger
from interfaces.dashboards.components.common.views import BaseView
from interfaces.dashboards.components.common.buttons import RefreshButton

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
        """Create the view with game server control buttons"""
        # Refresh button
        refresh_button = RefreshButton(
            callback=lambda i: self._handle_callback(i, "refresh"),
            label="Refresh"
        )
        self.add_item(refresh_button)
        
        # Server details button
        details_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Server Details",
            emoji="ℹ️",
            custom_id="server_details",
            row=0
        )
        details_button.callback = lambda i: self._handle_callback(i, "server_details")
        self.add_item(details_button)
        
        # Player list button
        players_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Player List",
            emoji="👥",
            custom_id="player_list",
            row=0
        )
        players_button.callback = lambda i: self._handle_callback(i, "player_list")
        self.add_item(players_button)
        
        # Server logs button
        logs_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="View Logs",
            emoji="📜",
            custom_id="server_logs",
            row=1
        )
        logs_button.callback = lambda i: self._handle_callback(i, "server_logs")
        self.add_item(logs_button)
        
        # Connection info button
        conn_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Connection Info",
            emoji="🔌",
            custom_id="connection_details",
            row=1
        )
        conn_button.callback = lambda i: self._handle_callback(i, "connection_details")
        self.add_item(conn_button)
        
        return self
    
    def _handle_callback(self, interaction: nextcord.Interaction, action: str):
        """Handle button callbacks through the callback registry"""
        # This will be handled by the set_callback mechanism
        logger.debug(f"Button {action} pressed, delegating to registered callback")
        pass
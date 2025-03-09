import nextcord
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from infrastructure.logging import logger
from interfaces.dashboards.components.common.views import BaseView
from interfaces.dashboards.components.common.buttons import RefreshButton

class MonitoringView(BaseView):
    """View for system monitoring dashboard with styled metrics and sections"""
    
    def __init__(
        self,
        metrics: Dict[str, Any] = None,
        timeout: Optional[int] = None
    ):
        super().__init__(timeout=timeout)
        self.metrics = metrics or {}
    
    def create_embed(self) -> nextcord.Embed:
        """Creates a beautifully formatted monitoring dashboard embed"""
        embed = nextcord.Embed(
            title="📊 System Dashboard",
            description="Current system performance and status",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        # Add server name and uptime if available
        if 'server_name' in self.metrics:
            embed.set_author(name=f"{self.metrics['server_name']} Status")
        
        # CPU Section with progress bar
        cpu_usage = self.metrics.get('cpu_usage', 0)
        cpu_bar = self._create_progress_bar(cpu_usage, 100)
        cpu_field = (
            f"**Usage:** {cpu_bar} {cpu_usage}%\n"
            f"**Model:** {self.metrics.get('cpu_model', 'Unknown')}\n"
            f"**Cores:** {self.metrics.get('cpu_cores', '?')} (Threads: {self.metrics.get('cpu_threads', '?')})\n"
            f"**Temp:** {self._colorize_temp(self.metrics.get('cpu_temp', 0))}°C"
        )
        embed.add_field(name="🖥️ CPU", value=cpu_field, inline=False)
        
        # Memory Section with progress bar
        memory_used = self.metrics.get('memory_used', 0)
        memory_bar = self._create_progress_bar(memory_used, 100)
        memory_field = (
            f"**Used:** {memory_bar} {memory_used}%\n"
            f"**Total:** {self.metrics.get('memory_total', '?')} GB"
        )
        embed.add_field(name="🧠 Memory", value=memory_field, inline=True)
        
        # Disk Section
        disk_free = self.metrics.get('disk_free', 0)
        disk_total = self.metrics.get('disk_total', 0)
        disk_used_percent = 100 - (disk_free/disk_total*100) if disk_total > 0 else 0
        disk_bar = self._create_progress_bar(disk_used_percent, 100)
        disk_field = (
            f"**Used:** {disk_bar} {disk_used_percent:.1f}%\n"
            f"**Free:** {disk_free:.2f} GB / {disk_total:.2f} GB"
        )
        embed.add_field(name="💾 Disk", value=disk_field, inline=True)
        
        # Network Section
        network_field = (
            f"**Internet:** ↓{self.metrics.get('net_download', '?')} Mbps, "
            f"↑{self.metrics.get('net_upload', '?')} Mbps (Ping: {self.metrics.get('net_ping', '?')}ms)\n"
            f"**LAN:** {self.metrics.get('lan_max', '?')}, "
            f"Current: ↑{self.metrics.get('lan_up', '?')}, ↓{self.metrics.get('lan_down', '?')}"
        )
        embed.add_field(name="🌐 Network", value=network_field, inline=False)
        
        # Services Section
        containers_running = self.metrics.get('containers_running', 0)
        containers_total = self.metrics.get('containers_total', 0) 
        containers_errors = self.metrics.get('containers_errors', 0)
        services_field = (
            f"**Docker:** {containers_running}/{containers_total} containers running\n"
            f"**Errors:** {'🟢 None' if containers_errors == 0 else f'🔴 {containers_errors}'}"
        )
        embed.add_field(name="🐳 Services", value=services_field, inline=True)
        
        # Game Servers Section with status indicators
        game_servers = self.metrics.get('game_servers', {})
        servers_list = []
        
        for name, data in game_servers.items():
            status_emoji = "✅" if data.get('online', False) else "❌"
            port_info = f"Port{'s' if len(data.get('ports', [])) > 1 else ''}: {', '.join(map(str, data.get('ports', [])))} " if data.get('online', False) else ""
            servers_list.append(f"• {status_emoji} **{name}**: {port_info}")
            
        servers_field = "\n".join(servers_list) if servers_list else "No game servers configured"
        embed.add_field(name="🎮 Game Servers", value=servers_field, inline=False)
        
        # Footer with last update time
        embed.set_footer(text=f"Last updated • {datetime.now().strftime('%H:%M:%S')} | Refresh for new data")
        
        return embed
    
    def _create_progress_bar(self, value: float, max_value: float, length: int = 10) -> str:
        """Creates a visual progress bar with emojis"""
        filled_blocks = int((value / max_value) * length)
        
        if filled_blocks <= length * 0.33:
            filled = "🟢" * filled_blocks
        elif filled_blocks <= length * 0.66:
            filled = "🟡" * filled_blocks
        else:
            filled = "🔴" * filled_blocks
            
        empty = "⚫" * (length - filled_blocks)
        return filled + empty
    
    def _colorize_temp(self, temp: float) -> str:
        """Returns colored temperature string based on value"""
        if temp < 60:
            return f"🟢 {temp}"
        elif temp < 80:
            return f"🟡 {temp}"
        else:
            return f"🔴 {temp}"
    
    def create(self):
        """Create the view with monitoring control buttons"""
        # Refresh button
        refresh_button = RefreshButton(
            callback=lambda i: self._handle_callback(i, "refresh"),
            label="Aktualisieren"
        )
        self.add_item(refresh_button)
        
        # Detail view buttons for different sections
        system_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="System Details",
            emoji="🖥️",
            custom_id="system_details",
            row=0
        )
        system_button.callback = lambda i: self._handle_callback(i, "system_details")
        self.add_item(system_button)
        
        docker_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Services",
            emoji="🐳",
            custom_id="docker_services",
            row=0
        )
        docker_button.callback = lambda i: self._handle_callback(i, "services")
        self.add_item(docker_button)
        
        games_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Game Servers",
            emoji="🎮",
            custom_id="game_servers",
            row=1
        )
        games_button.callback = lambda i: self._handle_callback(i, "games")
        self.add_item(games_button)
        
        logs_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            label="Error Logs",
            emoji="⚠️",
            custom_id="view_logs",
            row=1
        )
        logs_button.callback = lambda i: self._handle_callback(i, "logs")
        self.add_item(logs_button)
        
        return self

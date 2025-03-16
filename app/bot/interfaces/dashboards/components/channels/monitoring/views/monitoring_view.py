import nextcord
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.interfaces.dashboards.components.common.views import BaseView
from app.bot.interfaces.dashboards.components.common.buttons import RefreshButton

class MonitoringView(BaseView):
    """View for system monitoring dashboard with styled metrics and sections"""
    
    def __init__(self, metrics):
        super().__init__()
        self.metrics = metrics if isinstance(metrics, dict) else {}
    
    def create_embed(self) -> nextcord.Embed:
        """Creates a beautifully formatted monitoring dashboard embed"""
        embed = nextcord.Embed(
            title="📊 System Dashboard",
            description="Current system performance and status",
            color=0x3498db
        )
        
        # CPU Section
        cpu_model = self.metrics.get('cpu_model', 'Unknown')
        cpu_cores = self.metrics.get('cpu_cores', '?')
        cpu_threads = self.metrics.get('cpu_threads', '?') 
        cpu_usage = self.metrics.get('cpu_usage', 0)
        cpu_temp = self.metrics.get('cpu_temp', 0)
        
        cpu_bar = self._create_progress_bar(cpu_usage, 100)
        temp_indicator = "🟢" if cpu_temp < 60 else "🟡" if cpu_temp < 80 else "🔴"
        
        cpu_field = (
            f"**Usage:** {cpu_bar} {cpu_usage}%\n"
            f"**Model:** {cpu_model}\n"
            f"**Cores:** {cpu_cores} (Threads: {cpu_threads})\n"
            f"**Temp:** {temp_indicator} {cpu_temp}°C"
        )
        embed.add_field(name="💻 CPU", value=cpu_field, inline=False)
        
        # Memory Section
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
        
        for server_name, status in game_servers.items():
            if isinstance(status, dict):
                # New format
                is_online = status.get('online', False)
                ports = ', '.join(map(str, status.get('ports', []))) if status.get('ports') else 'N/A'
                servers_list.append(f"{'✅' if is_online else '❌'} {server_name}: {ports}")
            else:
                # Old string format
                servers_list.append(f"{server_name}: {status}")
        
        if servers_list:
            servers_text = "\n".join(servers_list)
        else:
            servers_text = "No game servers configured"
            
        embed.add_field(name="🎮 Game Servers", value=servers_text, inline=False)
        
        # Update timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        embed.set_footer(text=f"Last updated • {current_time} | Refresh for new data • heute um {(datetime.now() + timedelta(minutes=15)).strftime('%H:%M')} Uhr")
        
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

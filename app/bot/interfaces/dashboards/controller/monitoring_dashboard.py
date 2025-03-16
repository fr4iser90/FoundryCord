from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.channel_config import ChannelConfig
from app.bot.interfaces.dashboards.components.channels.monitoring.embeds import MonitoringEmbed
from app.bot.interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder
from .base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.components.channels.monitoring.views import MonitoringView
from app.bot.domain.monitoring.models.metric import SystemMetrics
from app.bot.interfaces.dashboards.components.common.embeds import DashboardEmbed
from app.bot.interfaces.dashboards.components.common.buttons import RefreshButton


class MonitoringDashboardController(BaseDashboardController):
    """UI class for displaying the monitoring dashboard"""
    
    DASHBOARD_TYPE = "monitoring"
    TITLE_IDENTIFIER = "System Status"
    
    def __init__(self, bot):
        super().__init__(bot)
        self.service = None
        self.initialized = False
        self.system_metrics = None
        self.last_metrics = {}
    
    def set_service(self, service):
        """Sets the service for this UI component"""
        self.service = service
        return self
    
    async def initialize(self):
        """Initialize the monitoring dashboard UI"""
        self.initialized = True
        logger.info("Monitoring Dashboard UI initialized")
        return await super().initialize(channel_config_key='monitoring')
    
    async def create_embed(self) -> nextcord.Embed:
        """Creates monitoring dashboard embed with system data"""
        if not self.service:
            logger.error("Monitoring service not available")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description="Monitoring service not available",
                color=0xff0000
            )
        
        try:
            # Fetch system status data
            logger.info("Hole System-Status-Daten...")
            raw_data = await self.service.get_system_status_dict()
            
            # Transform data to the expected format for MonitoringView
            self.last_metrics = self._transform_metrics(raw_data)
            logger.info(f"Transformierte Metrikdaten: {self.last_metrics}")
            
            # Create view with the transformed metrics
            monitoring_view = MonitoringView(self.last_metrics)
            embed = monitoring_view.create_embed()
            
            return embed
        except Exception as e:
            logger.error(f"Error creating monitoring embed: {str(e)}", exc_info=True)
            return self.create_error_embed(str(e))
    
    def _transform_metrics(self, raw_data):
        """Transformiert Rohmetriken in das von der View erwartete Format."""
        result = {}
        
        # Wenn keine Daten vorhanden, gib leeres Dictionary zurück
        if not raw_data:
            logger.warning("Keine Rohdaten erhalten, verwende Standardwerte")
            return result
        
        # Speichere alle Game-Server-Daten
        game_servers = {}
        
        # Verarbeite Listen von Metric-Objekten
        if isinstance(raw_data, list):
            for metric in raw_data:
                if hasattr(metric, 'name') and hasattr(metric, 'value'):

                    # Memory
                    if metric.name == 'memory_used' and hasattr(metric, 'unit') and metric.unit == 'bytes':
                        result[metric.name] = round(metric.value / (1024**3), 2)  # Bytes zu GB
                    elif metric.name == 'memory_total' and hasattr(metric, 'unit') and metric.unit == 'bytes':
                        result[metric.name] = round(metric.value / (1024**3), 2)  # Bytes zu GB
                    elif metric.name == 'memory_percent':
                        result['memory_percent'] = metric.value
                    
                    # CPU
                    elif metric.name == 'cpu_usage':
                        result['cpu_usage'] = metric.value
                    elif metric.name == 'cpu_temperature':
                        result['cpu_temp'] = metric.value
                    
                    # Docker/Container
                    elif metric.name == 'docker_running':
                        result['containers_running'] = metric.value
                    elif metric.name == 'docker_total':
                        result['containers_total'] = metric.value
                    elif metric.name == 'docker_errors':
                        result['containers_errors'] = metric.value
                    
                    # Disk - WICHTIG: Überprüfe die tatsächlichen Namen deiner Disk-Metriken
                    elif 'disk' in metric.name.lower() and 'free' in metric.name.lower():
                        # Konvertiere zu GB wenn in Bytes
                        if hasattr(metric, 'unit') and metric.unit == 'bytes':
                            result['disk_free'] = round(metric.value / (1024**3), 2)
                        else:
                            result['disk_free'] = metric.value
                    elif 'disk' in metric.name.lower() and 'total' in metric.name.lower():
                        # Konvertiere zu GB wenn in Bytes
                        if hasattr(metric, 'unit') and metric.unit == 'bytes':
                            result['disk_total'] = round(metric.value / (1024**3), 2)
                        else:
                            result['disk_total'] = metric.value
                    
                    # Netzwerk - WICHTIG: Überprüfe die tatsächlichen Namen deiner Netzwerk-Metriken
                    elif 'net' in metric.name.lower() and 'download' in metric.name.lower():
                        result['net_download'] = metric.value
                    elif 'net' in metric.name.lower() and 'upload' in metric.name.lower():
                        result['net_upload'] = metric.value
                    elif 'net' in metric.name.lower() and 'ping' in metric.name.lower():
                        result['net_ping'] = metric.value
                    elif 'lan' in metric.name.lower() and 'max' in metric.name.lower():
                        result['lan_max'] = metric.value
                    elif 'lan' in metric.name.lower() and 'up' in metric.name.lower():
                        result['lan_up'] = metric.value
                    elif 'lan' in metric.name.lower() and 'down' in metric.name.lower():
                        result['lan_down'] = metric.value
                    
                    # Game Server Informationen
                    elif metric.name == 'service_status' and hasattr(metric, 'service_name') and '🎮' in getattr(metric, 'service_name', ''):
                        server_name = getattr(metric, 'service_name', 'Unknown')
                        if metric.value == 1:
                            ports = getattr(metric, 'ports', [])
                            port_str = ', '.join(map(str, ports)) if ports else 'unknown'
                            game_servers[server_name] = f"✅ Online auf Port(s): {port_str}"
                        else:
                            game_servers[server_name] = "❌ Offline"
                    
                    # CPU Metrics
                    elif 'cpu' in metric.name.lower() and 'model' in metric.name.lower():
                        result['cpu_model'] = metric.value
                    elif 'cpu' in metric.name.lower() and 'cores' in metric.name.lower():
                        result['cpu_cores'] = metric.value
                    elif 'cpu' in metric.name.lower() and 'threads' in metric.name.lower():
                        result['cpu_threads'] = metric.value
                    
                    # Standard-Fall: Direkte Übernahme mit Debug-Info
                    else:
                        result[metric.name] = metric.value
                        
            
            # Game Server-Liste zum Ergebnis hinzufügen
            if game_servers:
                result['game_servers'] = game_servers
        
        # Falls bereits ein Dictionary übergeben wurde
        elif isinstance(raw_data, dict):
            result = raw_data
        
        logger.info(f"Transformierte Metriken: {result}")
        return result
    
    async def update_dashboard(self, interaction: Optional[nextcord.Interaction] = None):
        """Updates the monitoring dashboard with fresh data"""
        try:
            # Force cleanup before updating
            await self.cleanup_old_dashboards(keep_count=1)
            
            # Get system data
            raw_data = await self.service.get_system_status_dict()
            
            # Transform data using domain model
            try:
                system_metrics = SystemMetrics.from_raw_data(raw_data)
                metrics = system_metrics.to_dict()
                
                # Store metrics for button handlers to use
                self.last_metrics = metrics
                self.system_metrics = system_metrics  # Store the domain object too
                
                # Create view and embed using MonitoringView
                monitoring_view = MonitoringView(metrics)
                embed = monitoring_view.create_embed()
                view = monitoring_view.create()
                
                # Register button callbacks - MUST USE AWAIT like in welcome_dashboard
                await self.register_callbacks(view)
                
                # Update the dashboard
                if interaction:
                    await interaction.response.edit_message(embed=embed, view=view)
                else:
                    if self.message and hasattr(self.message, 'edit'):
                        try:
                            self.message = await self.message.edit(embed=embed, view=view)
                            logger.info(f"Updated existing monitoring dashboard in {self.channel.name}")
                        except Exception as e:
                            logger.warning(f"Couldn't update existing message: {e}, creating new")
                            self.message = await self.channel.send(embed=embed, view=view)
                    else:
                        self.message = await self.channel.send(embed=embed, view=view)
                        
                        # Track in dashboard manager - like in welcome_dashboard
                        await self.bot.dashboard_manager.track_message(
                            dashboard_type=self.DASHBOARD_TYPE,
                            message_id=self.message.id,
                            channel_id=self.channel.id
                        )
                
                return embed
                
            except Exception as e:
                logger.error(f"Error creating monitoring embed: {e}")
                # Use the error embed method
                error_embed = self.create_error_embed(str(e))
                
                if interaction:
                    await interaction.response.edit_message(embed=error_embed)
                else:
                    if self.message:
                        await self.message.edit(embed=error_embed)
                    else:
                        await self.channel.send(embed=error_embed)
            
        except Exception as e:
            logger.error(f"Error displaying monitoring dashboard: {e}")

    def _extract_ports(self, status_text):
        """Helper to extract port numbers from status text"""
        ports = []
        if 'Port' in status_text:
            try:
                port_section = status_text.split('Port')[1].split(':')[1].strip()
                ports = [int(p.strip()) for p in port_section.split(',') if p.strip().isdigit()]
            except (IndexError, ValueError):
                pass
        return ports
    
    async def on_system_details(self, interaction: nextcord.Interaction):
        """Show detailed system information"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "system_details"):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get system data (either from cached metrics or fresh)
            if hasattr(self, 'last_metrics'):
                metrics = self.last_metrics
            else:
                # KONSISTENTE BENENNUNG MIT _dict
                data = await self.service.get_system_status_dict()
                system_data = data.get('system', {})
                metrics = {
                    'cpu_model': system_data.get('hardware_info', {}).get('cpu_model', 'Unknown'),
                    'cpu_cores': system_data.get('hardware_info', {}).get('cpu_cores', '?'),
                    'cpu_threads': system_data.get('hardware_info', {}).get('cpu_threads', '?'),
                    'cpu_usage': system_data.get('cpu', 0),
                    'cpu_temp': system_data.get('cpu_temp', 0),
                    'cpu_freq_current': system_data.get('hardware_info', {}).get('cpu_freq_current', 'Unknown'),
                    'cpu_freq_min': system_data.get('hardware_info', {}).get('cpu_freq_min', 'Unknown'),
                    'cpu_freq_max': system_data.get('hardware_info', {}).get('cpu_freq_max', 'Unknown'),
                    'hardware_info': system_data.get('hardware_info', {})
                }
            
            # Create a beautiful table with system details
            cpu_table = UnicodeTableBuilder("CPU Details", width=50)
            cpu_table.add_header_row("Property", "Value")
            cpu_table.add_row("Model", metrics.get('cpu_model', 'Unknown'))
            cpu_table.add_row("Cores/Threads", f"{metrics.get('cpu_cores', '?')}/{metrics.get('cpu_threads', '?')}")
            cpu_table.add_row("Current Frequency", metrics.get('hardware_info', {}).get('cpu_freq_current', 'Unknown'))
            cpu_table.add_row("Min/Max Frequency", f"{metrics.get('hardware_info', {}).get('cpu_freq_min', 'Unknown')} / {metrics.get('hardware_info', {}).get('cpu_freq_max', 'Unknown')}")
            cpu_table.add_row("Current Usage", f"{metrics.get('cpu_usage', 0)}%")
            cpu_table.add_row("Temperature", f"{metrics.get('cpu_temp', 0)}°C")
            
            # Get sensor data for detailed temperature info
            temp_data = {}
            for key, value in metrics.get('hardware_info', {}).items():
                if key.startswith('temp_'):
                    temp_data[key.replace('temp_', '')] = value
            
            # Add temperature details if available
            if temp_data:
                cpu_table.add_divider()
                cpu_table.add_header_row("Temperature Sensors")
                for sensor, temp in temp_data.items():
                    if 'core' in sensor.lower() or 'cpu' in sensor.lower():
                        cpu_table.add_row(sensor, f"{temp}°C")
            
            # Send the table as a response
            await interaction.followup.send(cpu_table.build(), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying system details: {e}")
            await interaction.followup.send(f"Error displaying system details: {str(e)}", ephemeral=True)
    
    async def on_services(self, interaction: nextcord.Interaction):
        """Show services information"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "services"):
            return
        
        await interaction.response.defer()
        
        try:
            # Get services data
            data = await self.service.get_system_status_dict()
            service_data = data.get('services', {})
            
            # Create a table for Docker services
            docker_table = UnicodeTableBuilder("Docker Services", width=60)
            docker_table.add_header_row("Container", "Status", "Image", "Ports")
            
            # Add container data if available
            containers = service_data.get('containers', [])
            if containers:
                for container in containers:
                    name = container.get('name', 'Unknown')
                    status = container.get('status', 'Unknown')
                    image = container.get('image', 'Unknown')
                    ports = container.get('ports', '-')
                    docker_table.add_row(name, status, image, ports)
            else:
                docker_table.add_row("No container data available", "", "", "")
            
            # Send the table as a response
            await interaction.followup.send(docker_table.build(), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying services: {e}")
            await interaction.followup.send(f"Error displaying services: {str(e)}", ephemeral=True)
    
    async def on_games(self, interaction: nextcord.Interaction):
        """Show game servers information"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "games"):
            return
        
        await interaction.response.defer(ephemeral=True)

        try:
            # Get game servers data (either from cached metrics or fresh)
            if hasattr(self, 'last_metrics'):
                game_servers = self.last_metrics.get('game_servers', {})
            else:
                data = await self.service.get_system_status_dict()
                service_data = data.get('services', {})
                game_services = {}
                if 'services' in service_data:
                    game_services = {
                        name.replace('🎮 ', ''): {
                            'online': 'Online' in status or '✅' in status,
                            'ports': self._extract_ports(status)
                        }
                        for name, status in service_data.get('services', {}).items() 
                        if '🎮' in name
                    }
                game_servers = game_services
            
            # Create a table for game servers
            games_table = UnicodeTableBuilder("Game Servers Status", width=50)
            games_table.add_header_row("Server", "Status", "Ports")
            
            if game_servers:
                for name, info in game_servers.items():
                    status = "✅ Online" if info.get('online') else "❌ Offline"
                    ports = ", ".join(map(str, info.get('ports', []))) or "N/A"
                    games_table.add_row(name, status, ports)
            else:
                games_table.add_row("No game servers configured", "", "")
            
            # Send the table as a response
            await interaction.followup.send(games_table.build(), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying game servers: {e}")
            await interaction.followup.send(f"Error displaying game servers: {str(e)}", ephemeral=True)
    
    async def on_logs(self, interaction: nextcord.Interaction):
        """Show error logs"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "logs"):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get error logs from service (implement this method in your service)
            logs = await self.service.get_system_logs(limit=10, level='ERROR')
            
            if not logs:
                await interaction.followup.send("No error logs found.", ephemeral=True)
                return
            
            # Create a table for error logs
            logs_table = UnicodeTableBuilder("Recent Error Logs", width=60)
            logs_table.add_header_row("Timestamp", "Message", "Source")
            
            for log in logs:
                timestamp = log.get('timestamp', 'Unknown')
                message = log.get('message', 'Unknown error')[:30] + "..." if len(log.get('message', '')) > 30 else log.get('message', 'Unknown error')
                source = log.get('source', 'Unknown')
                logs_table.add_row(timestamp, message, source)
            
            # Send the table as a response
            await interaction.followup.send(logs_table.build(), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error displaying logs: {e}")
            await interaction.followup.send(f"Error displaying logs: {str(e)}", ephemeral=True)
    
    async def register_callbacks(self, view):
        """Register button callbacks for the monitoring dashboard"""
        # Find the buttons by their custom_id and assign callbacks
        for item in view.children:
            if hasattr(item, 'custom_id'):
                if item.custom_id == "system_details":
                    item.callback = self.on_system_details
                elif item.custom_id == "docker_services":
                    item.callback = self.on_services
                elif item.custom_id == "game_servers":
                    item.callback = self.on_games
                elif item.custom_id == "view_logs":
                    item.callback = self.on_logs
                
        # Also register the refresh button if exists
        for item in view.children:
            if isinstance(item, RefreshButton):
                item.callback = self.on_refresh
            
        return view

    def create_view(self) -> nextcord.ui.View:
        """Create a view with monitoring buttons"""
        if hasattr(self, 'last_metrics') and self.last_metrics:
            # Create view with metrics
            monitoring_view = MonitoringView(self.last_metrics)
            view = monitoring_view.create()
            
            # Register callbacks
            view.set_callback("refresh", self.on_refresh)
            view.set_callback("system_details", self.on_system_details)
            view.set_callback("services", self.on_services)
            view.set_callback("games", self.on_games)
            view.set_callback("logs", self.on_logs)
            
            return view
        else:
            return super().create_view()

    def create_error_embed(self, error_message: str) -> nextcord.Embed:
        """Creates an error embed for the monitoring dashboard"""
        embed = nextcord.Embed(
            title="⚠️ System Monitoring Error",
            description=f"An error occurred while collecting system data:\n```{error_message}```",
            color=0xff0000
        )
        
        # Add standard footer
        DashboardEmbed.add_standard_footer(embed)
        
        return embed

    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the refresh button"""
        # Check rate limiting first
        if not await self.check_rate_limit(interaction, "refresh"):
            return
        
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Fetch new metrics data from service
            raw_data = await self.service.get_system_status_dict()
            self.last_metrics = self._transform_metrics(raw_data)
            
            # Create new embed with updated data
            embed = await self.create_embed()
            view = self.create_view()
            
            # Update the message
            await interaction.message.edit(content=None, embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error refreshing monitoring dashboard: {e}")
            await interaction.followup.send(
                f"Fehler beim Aktualisieren: {str(e)}",
                ephemeral=True
            )

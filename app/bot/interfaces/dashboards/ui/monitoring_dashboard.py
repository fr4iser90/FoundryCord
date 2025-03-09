from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.channels.monitoring.embeds import MonitoringEmbed
from interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.channels.monitoring.views import MonitoringView

class MonitoringDashboardUI(BaseDashboardUI):
    """UI class for displaying the monitoring dashboard"""
    
    DASHBOARD_TYPE = "monitoring"
    TITLE_IDENTIFIER = "System Status"
    
    async def initialize(self):
        """Initialize the monitoring dashboard UI"""
        return await super().initialize(channel_config_key='monitoring')
    
    async def create_embed(self) -> nextcord.Embed:
        """Creates monitoring dashboard embed with system data"""
        if not self.service:
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description="Monitoring service not available",
                color=0xff0000
            )
        
        # Get data DIRECTLY
        data = await self.service.get_system_status()
        
        # Transform data for the monitoring embed
        system_data = data.get('system', {})
        service_data = data.get('services', {})
        
        # Create comprehensive metrics dictionary for enhanced view
        metrics = {
            # CPU metrics
            'cpu_usage': system_data.get('cpu', 0),
            'cpu_model': system_data.get('hardware_info', {}).get('cpu_model', 'Unknown'),
            'cpu_cores': system_data.get('hardware_info', {}).get('cpu_cores', '?'),
            'cpu_threads': system_data.get('hardware_info', {}).get('cpu_threads', '?'),
            'cpu_temp': system_data.get('cpu_temp', 0),
            
            # Memory metrics
            'memory_used': system_data.get('memory', {}).percent if hasattr(system_data.get('memory', {}), 'percent') else 0,
            'memory_total': round(system_data.get('memory', {}).total / (1024**3), 1) if hasattr(system_data.get('memory', {}), 'total') else 0,
            
            # Disk metrics
            'disk_free': round(system_data.get('disk', {}).free / (1024**3), 2) if hasattr(system_data.get('disk', {}), 'free') else 0,
            'disk_total': round(system_data.get('disk', {}).total / (1024**3), 2) if hasattr(system_data.get('disk', {}), 'total') else 0,
            
            # Network metrics
            'net_download': getattr(system_data.get('network', {}), 'download_speed', 0),
            'net_upload': getattr(system_data.get('network', {}), 'upload_speed', 0),
            'net_ping': getattr(system_data.get('network', {}), 'ping', 0),
            
            # If you have LAN metrics
            'lan_max': getattr(system_data.get('network', {}), 'max_speed', '?'),
            'lan_up': getattr(system_data.get('network', {}), 'lan_upload', '?'),
            'lan_down': getattr(system_data.get('network', {}), 'lan_download', '?'),
            
            # Docker/container metrics
            'containers_running': service_data.get('docker_running', 0),
            'containers_total': service_data.get('docker_total', 0),
            'containers_errors': service_data.get('docker_errors', 0),
            
            # Game servers
            'game_servers': {},
            
            # Add hardware info for detailed views
            'hardware_info': system_data.get('hardware_info', {})
        }
        
        # Process game servers data
        if 'services' in service_data:
            game_services = {
                name.replace('🎮 ', ''): {
                    'online': 'Online' in status or '✅' in status,
                    'ports': self._extract_ports(status)
                }
                for name, status in service_data.get('services', {}).items() 
                if '🎮' in name
            }
            metrics['game_servers'] = game_services
        
        # Store metrics for button handlers to use
        self.last_metrics = metrics
        
        # Create view and embed using MonitoringView
        monitoring_view = MonitoringView(metrics)
        embed = monitoring_view.create_embed()
        
        return embed
    
    async def update_dashboard(self, interaction: Optional[nextcord.Interaction] = None):
        """Updates the monitoring dashboard with fresh data"""
        try:
            # Force cleanup before updating
            await self.cleanup_old_dashboards(keep_count=1)
            
            # Get raw data from service
            data = await self.service.get_system_status()
            
            # Transform data for the monitoring embed
            system_data = data.get('system', {})
            service_data = data.get('services', {})
            
            # Create comprehensive metrics dictionary for enhanced view
            metrics = {
                # CPU metrics
                'cpu_usage': system_data.get('cpu', 0),
                'cpu_model': system_data.get('hardware_info', {}).get('cpu_model', 'Unknown'),
                'cpu_cores': system_data.get('hardware_info', {}).get('cpu_cores', '?'),
                'cpu_threads': system_data.get('hardware_info', {}).get('cpu_threads', '?'),
                'cpu_temp': system_data.get('cpu_temp', 0),
                
                # Memory metrics
                'memory_used': system_data.get('memory', {}).percent if hasattr(system_data.get('memory', {}), 'percent') else 0,
                'memory_total': round(system_data.get('memory', {}).total / (1024**3), 1) if hasattr(system_data.get('memory', {}), 'total') else 0,
                
                # Disk metrics
                'disk_free': round(system_data.get('disk', {}).free / (1024**3), 2) if hasattr(system_data.get('disk', {}), 'free') else 0,
                'disk_total': round(system_data.get('disk', {}).total / (1024**3), 2) if hasattr(system_data.get('disk', {}), 'total') else 0,
                
                # Network metrics
                'net_download': getattr(system_data.get('network', {}), 'download_speed', 0),
                'net_upload': getattr(system_data.get('network', {}), 'upload_speed', 0),
                'net_ping': getattr(system_data.get('network', {}), 'ping', 0),
                
                # If you have LAN metrics
                'lan_max': getattr(system_data.get('network', {}), 'max_speed', '?'),
                'lan_up': getattr(system_data.get('network', {}), 'lan_upload', '?'),
                'lan_down': getattr(system_data.get('network', {}), 'lan_download', '?'),
                
                # Docker/container metrics
                'containers_running': service_data.get('docker_running', 0),
                'containers_total': service_data.get('docker_total', 0),
                'containers_errors': service_data.get('docker_errors', 0),
                
                # Game servers
                'game_servers': {},
                
                # Add hardware info for detailed views
                'hardware_info': system_data.get('hardware_info', {})
            }
            
            # Process game servers data
            if 'services' in service_data:
                game_services = {
                    name.replace('🎮 ', ''): {
                        'online': 'Online' in status or '✅' in status,
                        'ports': self._extract_ports(status)
                    }
                    for name, status in service_data.get('services', {}).items() 
                    if '🎮' in name
                }
                metrics['game_servers'] = game_services
            
            # Store metrics for button handlers to use
            self.last_metrics = metrics
            
            # Create view and embed using MonitoringView
            monitoring_view = MonitoringView(metrics)
            embed = monitoring_view.create_embed()
            view = monitoring_view.create()
            
            # Register button callbacks
            await self.register_callbacks(view)
            
            # Update the dashboard
            if interaction:
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                self.message = await self.channel.send(embed=embed, view=view) if not self.message else await self.message.edit(embed=embed, view=view)
            
            return embed
            
        except Exception as e:
            logger.error(f"Error updating monitoring dashboard: {e}")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description=f"Error updating dashboard: {str(e)}",
                color=0xff0000
            )

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
        await interaction.response.defer()
        
        try:
            # Get system data (either from cached metrics or fresh)
            if hasattr(self, 'last_metrics'):
                metrics = self.last_metrics
            else:
                data = await self.service.get_system_status()
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
        await interaction.response.defer()
        
        try:
            # Get services data
            data = await self.service.get_system_status()
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
        await interaction.response.defer()
        
        try:
            # Get game servers data (either from cached metrics or fresh)
            if hasattr(self, 'last_metrics'):
                game_servers = self.last_metrics.get('game_servers', {})
            else:
                data = await self.service.get_system_status()
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
        await interaction.response.defer()
        
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
        """Register callbacks for the view's buttons"""
        view.set_callback("refresh", self.on_refresh)
        view.set_callback("system_details", self.on_system_details)
        view.set_callback("services", self.on_services)
        view.set_callback("games", self.on_games)
        view.set_callback("logs", self.on_logs)

    def create_view(self) -> nextcord.ui.View:
        """Create a view with monitoring buttons"""
        if hasattr(self, 'last_metrics') and self.last_metrics:
            # Create view with metrics
            monitoring_view = MonitoringView(self.last_metrics)
            view = monitoring_view.create()
            
            # Register callbacks
            view.set_callback("refresh", self.on_refresh)  # Use base class method!
            view.set_callback("system_details", self.on_system_details)
            view.set_callback("services", self.on_services)
            view.set_callback("games", self.on_games)
            view.set_callback("logs", self.on_logs)
            
            return view
        else:
            # Fallback to base view
            return super().create_view()

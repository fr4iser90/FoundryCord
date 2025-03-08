from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.embeds.monitoring_embed import MonitoringEmbed
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.views.enhanced_monitoring_view import EnhancedMonitoringView

class MonitoringDashboardUI(BaseDashboardUI):
    """UI class for displaying the monitoring dashboard"""
    
    DASHBOARD_TYPE = "monitoring"
    TITLE_IDENTIFIER = "System Status"
    
    async def initialize(self):
        """Initialize the monitoring dashboard UI"""
        return await super().initialize(channel_config_key='monitoring')
    
    async def create_embed(self) -> nextcord.Embed:
        """Creates the monitoring dashboard embed with system data"""
        if not self.service:
            logger.error("No service available for MonitoringDashboard")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description="Monitoring service not available",
                color=0xff0000
            )
        
        try:
            # Get raw data from service
            data = await self.service.get_system_status()
            
            # Transform data for the monitoring embed
            system_data = data.get('system', {})
            service_data = data.get('services', {})
            
            # Create formatted data dictionary for the embed
            formatted_data = {
                # CPU data - direct from psutil
                'cpu_usage': system_data.get('cpu'),
                
                # Memory data
                'memory_usage': system_data.get('memory').percent if hasattr(system_data.get('memory', {}), 'percent') else 'N/A',
                
                # Disk data
                'disk_free': round(system_data.get('disk').free / (1024**3), 2) if hasattr(system_data.get('disk', {}), 'free') else 'N/A',
            }
            
            # Create the embed using your existing component
            embed = MonitoringEmbed.create_system_status(formatted_data)
            
            # Add supplementary fields to the embed
            if system_data.get('hardware_info'):
                hardware = system_data['hardware_info']
                cpu_info = f"Model: {hardware.get('cpu_model', 'N/A')}\n"
                cpu_info += f"Cores: {hardware.get('cpu_cores', 'N/A')} (Threads: {hardware.get('cpu_threads', 'N/A')})\n"
                cpu_info += f"Temp: {system_data.get('cpu_temp', 'N/A')}°C"
                embed.add_field(name="CPU Details", value=cpu_info, inline=False)
                
                if 'network_adapters' in hardware:
                    embed.add_field(name="Network", value=hardware['network_adapters'], inline=False)
            
            # Add services information
            if service_data:
                services_text = ""
                if 'docker_running' in service_data:
                    services_text += f"• Running containers: {service_data['docker_running']}\n"
                if 'docker_errors' in service_data:
                    services_text += f"• Container errors: {service_data['docker_errors']}\n"
                
                # Add game services info
                if 'services' in service_data:
                    game_services = [s for s in service_data['services'].items() if '🎮' in s[0]]
                    if game_services:
                        services_text += "\nGame Servers:\n"
                        for name, status in game_services:
                            services_text += f"• {name}: {status}\n"
                
                if services_text:
                    embed.add_field(name="Services", value=services_text, inline=False)
            
            # Add timestamp to footer
            embed.set_footer(text=f"heute um {datetime.now().strftime('%H:%M')} Uhr")
            
            return embed
        except Exception as e:
            logger.error(f"Error creating monitoring embed: {e}")
            return nextcord.Embed(
                title="⚠️ Dashboard Error",
                description=f"Error creating monitoring dashboard: {str(e)}",
                color=0xff0000
            )

    async def update_dashboard(self, interaction: Optional[nextcord.Interaction] = None):
        """Updates the monitoring dashboard with fresh data"""
        try:
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
                'game_servers': {}
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
            
            # Create enhanced view and embed
            monitoring_view = EnhancedMonitoringView(metrics)
            embed = monitoring_view.create_embed()
            view = monitoring_view.create()
            
            # Update the dashboard
            if interaction:
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await self.update_message(embed=embed, view=view)
                
        except Exception as e:
            logger.error(f"Error updating monitoring dashboard: {e}")
            error_embed = nextcord.Embed(
                title="⚠️ Dashboard Error",
                description=f"Error updating dashboard: {str(e)}",
                color=0xff0000
            )
            if interaction:
                await interaction.response.edit_message(embed=error_embed)
            else:
                await self.update_message(embed=error_embed)
    
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

    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handle refresh button click"""
        await interaction.response.defer()
        await self.update_dashboard(interaction)
    
    async def on_system_details(self, interaction: nextcord.Interaction):
        """Show detailed system information"""
        # Create a more detailed system view/embed 
        await interaction.response.defer()
        # Implement system details view
    
    async def on_services(self, interaction: nextcord.Interaction):
        """Show services information"""
        await interaction.response.defer()
        # Implement services details view
    
    async def on_games(self, interaction: nextcord.Interaction):
        """Show game servers information"""
        await interaction.response.defer()
        # Implement game servers details view
    
    async def on_logs(self, interaction: nextcord.Interaction):
        """Show error logs"""
        await interaction.response.defer()
        # Implement error logs view
    
    async def register_callbacks(self, view):
        """Register callbacks for the view's buttons"""
        view.set_callback("refresh", self.on_refresh)
        view.set_callback("system_details", self.on_system_details)
        view.set_callback("services", self.on_services)
        view.set_callback("games", self.on_games)
        view.set_callback("logs", self.on_logs)

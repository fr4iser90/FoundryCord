from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.embeds import MonitoringEmbed
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.views import MonitoringView

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
        
        # Simply call update_dashboard to use the enhanced view for initial display too
        return await self.update_dashboard()
    
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
            
            # Create view and embed using MonitoringView instead of EnhancedMonitoringView
            monitoring_view = MonitoringView(metrics)
            embed = monitoring_view.create_embed()
            view = monitoring_view.create()
            
            # Update the dashboard
            if interaction:
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                # Use display_dashboard from BaseDashboardUI instead of update_message
                self.message = await self.channel.send(embed=embed, view=view) if not self.message else await self.message.edit(embed=embed, view=view)
            
            return embed  # Return the embed for create_embed to use
            
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

    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handle refresh button click"""
        await interaction.response.defer()
        
        # Get fresh data and create new embed/view
        data = await self.service.get_system_status()
        
        # Transform data for metrics (all your existing code)
        system_data = data.get('system', {})
        service_data = data.get('services', {})
        
        # Create comprehensive metrics dictionary
        metrics = {
            # Your existing metrics code
        }
        
        # Process game servers data
        if 'services' in service_data:
            game_services = {
                # Your existing game_services code
            }
            metrics['game_servers'] = game_services
        
        # Create view and embed
        monitoring_view = MonitoringView(metrics)
        embed = monitoring_view.create_embed()
        view = monitoring_view.create()
        
        # Use followup instead of response since we already deferred
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=embed,
            view=view
        )
    
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

from typing import Dict, Any, Optional, List
import nextcord
from datetime import datetime, timedelta
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.embeds.monitoring_embed import MonitoringEmbed
from .base_dashboard import BaseDashboardUI

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

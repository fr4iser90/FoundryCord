from typing import Dict, Any
import nextcord
from datetime import datetime
from app.bot.interfaces.dashboards.components.common.embeds import BaseEmbed

class MonitoringEmbed(BaseEmbed):
    """Monitoring specific embed implementations"""
    
    @classmethod
    def create_system_status(cls, status_data: Dict[str, Any]) -> nextcord.Embed:
        """Creates the system monitoring embed"""
        fields = {
            "CPU": {
                "value": f"Usage: {status_data.get('cpu_usage', 'N/A')}%",
                "inline": True
            },
            "Memory": {
                "value": f"Used: {status_data.get('memory_usage', 'N/A')}%",
                "inline": True
            },
            "Disk": {
                "value": f"Free: {status_data.get('disk_free', 'N/A')}GB",
                "inline": True
            }
        }
        
        return cls.create(
            title="🖥️ System Status",
            description="Current system metrics and status",
            fields=fields,
            color=cls.INFO_COLOR
        )
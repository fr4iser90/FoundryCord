from typing import Dict, Any, Optional
import nextcord
from datetime import datetime
from .base_embed import BaseEmbed

class StatusEmbed(BaseEmbed):
    """Status specific embed implementations"""
    
    @classmethod
    def create_status(
        cls,
        service_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> nextcord.Embed:
        """Creates a service status embed"""
        status_colors = {
            "online": cls.SUCCESS_COLOR,
            "offline": cls.ERROR_COLOR,
            "maintenance": cls.WARNING_COLOR,
            "degraded": cls.WARNING_COLOR
        }
        
        status_emojis = {
            "online": "🟢",
            "offline": "🔴",
            "maintenance": "🟡",
            "degraded": "🟠"
        }
        
        embed = cls.create(
            title=f"Service Status: {service_name}",
            description=f"Status: {status_emojis.get(status, '⚪')} {status.capitalize()}",
            color=status_colors.get(status, cls.DEFAULT_COLOR),
            timestamp=timestamp or datetime.now()
        )
        
        if details:
            for key, value in details.items():
                embed.add_field(
                    name=key.capitalize(),
                    value=str(value),
                    inline=True
                )
                
        return embed

    @classmethod
    def create_status_overview(cls, services: Dict[str, Dict[str, Any]]) -> nextcord.Embed:
        """Creates an overview of all service statuses"""
        embed = cls.create(
            title="🖥️ Service Status Overview",
            description="Current status of all services",
            color=cls.INFO_COLOR
        )
        
        for service_name, service_data in services.items():
            status = service_data.get('status', 'unknown')
            uptime = service_data.get('uptime', 'N/A')
            last_check = service_data.get('last_check', 'N/A')
            
            status_emoji = {
                "online": "🟢",
                "offline": "🔴",
                "maintenance": "🟡",
                "degraded": "🟠"
            }.get(status, "⚪")
            
            embed.add_field(
                name=f"{status_emoji} {service_name}",
                value=f"Status: {status.capitalize()}\n"
                      f"Uptime: {uptime}\n"
                      f"Last Check: {last_check}",
                inline=True
            )
            
        return embed

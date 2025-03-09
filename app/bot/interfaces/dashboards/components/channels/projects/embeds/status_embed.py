from typing import Dict, Any, Optional
import nextcord
from datetime import datetime
from interfaces.dashboards.components.common.embeds import BaseEmbed

class StatusEmbed(BaseEmbed):
    """Status specific embed implementations with consistent formatting"""
    
    @classmethod
    def create_status(
        cls,
        service_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> nextcord.Embed:
        """Creates a service status embed with consistent formatting"""
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
        
        embed = nextcord.Embed(
            title=f"Service Status: {service_name}",
            description=f"Status: {status_emojis.get(status, '⚪')} {status.capitalize()}",
            color=status_colors.get(status, cls.DEFAULT_COLOR),
            timestamp=timestamp or datetime.now()
        )
        
        if details:
            for key, value in details.items():
                # Format uptime with emoji
                if key.lower() == 'uptime':
                    embed.add_field(
                        name=f"⏱️ {key.capitalize()}",
                        value=str(value),
                        inline=True
                    )
                # Format usage with progress bar if it's a percentage
                elif 'usage' in key.lower() and isinstance(value, (int, float)):
                    progress_bar = cls._create_progress_bar(value, 100)
                    embed.add_field(
                        name=f"📊 {key.capitalize()}",
                        value=f"{progress_bar} {value}%",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=key.capitalize(),
                        value=str(value),
                        inline=True
                    )
                
        return embed

    @classmethod
    def create_status_overview(cls, services: Dict[str, Dict[str, Any]]) -> nextcord.Embed:
        """Creates an overview of all service statuses with consistent formatting"""
        embed = nextcord.Embed(
            title="🖥️ Service Status Overview",
            description="Current status of all services",
            color=cls.INFO_COLOR,
            timestamp=datetime.now()
        )
        
        # Group services by status for better organization
        status_groups = {
            "online": [],
            "degraded": [],
            "maintenance": [],
            "offline": []
        }
        
        for service_name, service_data in services.items():
            status = service_data.get('status', 'unknown')
            if status in status_groups:
                status_groups[status].append((service_name, service_data))
            else:
                status_groups.setdefault('unknown', []).append((service_name, service_data))
        
        # Add fields for each status group
        for status, services_list in status_groups.items():
            if not services_list:
                continue
                
            status_emoji = {
                "online": "🟢",
                "offline": "🔴",
                "maintenance": "🟡",
                "degraded": "🟠",
                "unknown": "⚪"
            }.get(status, "⚪")
            
            field_value = ""
            for service_name, service_data in services_list:
                uptime = service_data.get('uptime', 'N/A')
                last_check = service_data.get('last_check', 'N/A')
                
                field_value += f"**{service_name}**\n"
                field_value += f"└ Uptime: {uptime} | Last Check: {last_check}\n\n"
            
            embed.add_field(
                name=f"{status_emoji} {status.capitalize()} Services",
                value=field_value,
                inline=False
            )
        
        embed.set_footer(text=f"Last updated • {datetime.now().strftime('%H:%M:%S')}")
        return embed
    
    @staticmethod
    def _create_progress_bar(value: float, max_value: float, length: int = 10) -> str:
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
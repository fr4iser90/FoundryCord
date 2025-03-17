"""Status indicator component for dashboards."""
from typing import Dict, Any, Optional
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from .base_component import DashboardComponent

class StatusIndicatorComponent(DashboardComponent):
    """Component to display status indicators (e.g., online/offline)"""
    
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]) -> None:
        """Render status indicator to embed."""
        try:
            # Extract configuration
            title = config.get('title', 'Status')
            icon_map = config.get('icon_map', {
                'online': '✅',
                'offline': '❌',
                'warning': '⚠️',
                'error': '🔴',
                'unknown': '❓'
            })
            
            # Get status from data
            status = 'unknown'
            if data:
                status_field = config.get('status_field', 'status')
                status = str(data.get(status_field, 'unknown')).lower()
            
            # Get icon for status
            icon = icon_map.get(status, icon_map.get('unknown', '❓'))
            
            # Format message
            message = config.get('message_format', '{icon} {status}')
            formatted_message = message.format(
                icon=icon,
                status=status.capitalize(),
                **data if isinstance(data, dict) else {}
            )
            
            # Add to embed
            embed.add_field(
                name=title,
                value=formatted_message,
                inline=config.get('inline', True)
            )
            
        except Exception as e:
            logger.error(f"Error rendering status indicator: {e}")
            embed.add_field(
                name="Status Error",
                value="❌ Could not display status",
                inline=True
            )
    
    async def create_ui_component(self, view: nextcord.ui.View, data: Any,
                                 config: Dict[str, Any], dashboard_id: str) -> Optional[nextcord.ui.Item]:
        """Status indicators don't have UI components."""
        return None
    
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any,
                           config: Dict[str, Any], dashboard_id: str) -> None:
        """Status indicators don't have interactions."""
        pass 
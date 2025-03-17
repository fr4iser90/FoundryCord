"""Metric display component for dashboards."""
from typing import Dict, Any, Optional
import nextcord
import re

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from .base_component import DashboardComponent

class MetricDisplayComponent(DashboardComponent):
    """Component to display numeric metrics with formatting and thresholds"""
    
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]) -> None:
        """Render metric display to embed."""
        try:
            # Extract configuration
            title = config.get('title', 'Metric')
            format_string = config.get('format', '{value}')
            icon = config.get('icon', '')
            
            # Access nested data if metric_path is provided
            metric_path = config.get('metric_path', '')
            value = self._get_nested_value(data, metric_path) if data else None
            
            if value is None:
                value = 'N/A'
                
            # Format the value
            try:
                formatted_value = format_string.format(value=value)
            except (ValueError, TypeError):
                formatted_value = f"{value}"
                
            # Apply color based on thresholds if numeric
            color_indicator = ''
            if isinstance(value, (int, float)) and 'thresholds' in config:
                thresholds = config['thresholds']
                
                if 'critical' in thresholds and value >= thresholds['critical']:
                    color_indicator = '🔴'
                elif 'warning' in thresholds and value >= thresholds['warning']:
                    color_indicator = '🟠'
                elif 'good' in thresholds and value <= thresholds['good']:
                    color_indicator = '🟢'
                
            # Combine icon, color indicator, and formatted value
            display_value = f"{icon} {color_indicator} {formatted_value}".strip()
            
            # Add to embed
            embed.add_field(
                name=title,
                value=display_value,
                inline=config.get('inline', True)
            )
            
        except Exception as e:
            logger.error(f"Error rendering metric display: {e}")
            embed.add_field(
                name=config.get('title', 'Metric Error'),
                value="❌ Could not display metric",
                inline=True
            )
    
    async def create_ui_component(self, view: nextcord.ui.View, data: Any,
                                 config: Dict[str, Any], dashboard_id: str) -> Optional[nextcord.ui.Item]:
        """Metric displays don't have UI components."""
        return None
    
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any,
                           config: Dict[str, Any], dashboard_id: str) -> None:
        """Metric displays don't have interactions."""
        pass
        
    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Get a value from nested dictionaries using dot notation."""
        if not path or not data:
            return data
            
        parts = path.split('.')
        current = data
        
        for part in parts:
            # Handle array indexing with [index]
            match = re.match(r'(.+)\[(\d+)\]', part)
            if match:
                name, index = match.groups()
                index = int(index)
                
                if name in current and isinstance(current[name], (list, tuple)) and index < len(current[name]):
                    current = current[name][index]
                else:
                    return None
            # Regular dictionary access
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current 
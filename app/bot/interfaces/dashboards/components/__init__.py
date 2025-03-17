"""
Dashboard components package.
Provides UI components for dashboard interfaces.
"""
# Re-export common components
from .common.embeds.dashboard_embed import DashboardEmbed
from .common.embeds.error_embed import ErrorEmbed
from .common.buttons.refresh_button import RefreshButton
from .base_component import BaseComponent, DashboardComponent

# Import channels module for backward compatibility
from . import channels

# Export symbols
__all__ = [
    'BaseComponent',
    'DashboardComponent',
    'DashboardEmbed',
    'ErrorEmbed',
    'RefreshButton',
    'channels'  # Include for backward compatibility
] 
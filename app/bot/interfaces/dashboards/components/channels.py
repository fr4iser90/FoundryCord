"""
Compatibility module for legacy code that imports dashboard channels.
This provides a bridge to the new data-driven structure.
"""
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

logger.warning("Using deprecated channels module - use database components instead")

# If you know what specific components were previously defined in this module,
# you can re-export them from their new locations or create stub implementations

# For example:
class ChannelComponentStub:
    """Stub implementation for backward compatibility."""
    
    @staticmethod
    def get_component(component_id, **kwargs):
        logger.warning(f"Attempted to use legacy component: {component_id}")
        return None

# Export commonly used components that might have been in the old module
from app.bot.interfaces.dashboards.components.common.embeds import DashboardEmbed, ErrorEmbed
from app.bot.interfaces.dashboards.components.common.buttons.refresh_button import RefreshButton

# You can add more exports as needed based on what was in the original module

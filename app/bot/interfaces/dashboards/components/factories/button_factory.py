"""Button factory for creating button UI components."""
from typing import Dict, Any, Optional
import nextcord

from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

from app.bot.interfaces.dashboards.components.common.buttons.generic_button import GenericButtonComponent

from app.bot.infrastructure.factories.base.base_factory import BaseFactory

class ButtonFactory(BaseFactory):
    """Factory for creating button UI components."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def create(self, label: str, custom_id: str = None, style: str = "primary", 
              emoji: str = None, disabled: bool = False, **kwargs):
        """Create a button component."""
        try:
            # Convert style string to ButtonStyle enum
            button_style = self._get_button_style(style)
            
            # Create button
            button = nextcord.ui.Button(
                label=label,
                custom_id=custom_id,
                style=button_style,
                emoji=emoji,
                disabled=disabled,
                **kwargs
            )
            
            return button
            
        except Exception as e:
            logger.error(f"Error creating button: {e}")
            return None
    
    def _get_button_style(self, style_name: str) -> nextcord.ButtonStyle:
        """Convert style name to ButtonStyle enum."""
        styles = {
            "primary": nextcord.ButtonStyle.primary,
            "secondary": nextcord.ButtonStyle.secondary,
            "success": nextcord.ButtonStyle.success,
            "danger": nextcord.ButtonStyle.danger,
            "link": nextcord.ButtonStyle.link
        }
        
        return styles.get(style_name.lower(), nextcord.ButtonStyle.primary)
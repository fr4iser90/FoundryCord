import nextcord
from typing import Optional, Callable, Dict, Any
from app.shared.logging import logger

class BaseView(nextcord.ui.View):
    """Base class for all dashboard views"""
    
    def __init__(self, timeout: Optional[int] = None):
        super().__init__(timeout=timeout)
        self.callbacks: Dict[str, Callable] = {}
        
    def set_callback(self, action: str, callback: Callable):
        """Register a callback for a specific action"""
        self.callbacks[action] = callback
        
    async def _handle_callback(
        self, 
        interaction: nextcord.Interaction, 
        action: str,
        **kwargs: Any
    ):
        """Generic callback handler with error handling"""
        try:
            if action in self.callbacks:
                await self.callbacks[action](interaction, **kwargs)
            else:
                logger.warning(f"No callback registered for action: {action}")
                await interaction.response.send_message(
                    "Diese Aktion ist nicht verfügbar",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in view callback: {e}")
            await interaction.response.send_message(
                "Ein Fehler ist aufgetreten",
                ephemeral=True
            )

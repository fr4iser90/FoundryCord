import nextcord
from typing import Optional, Dict, Any
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class BaseModal(nextcord.ui.Modal):
    """Base class for all dashboard modals"""
    
    def __init__(
        self,
        title: str,
        custom_id: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        super().__init__(
            title=title,
            custom_id=custom_id,
            timeout=timeout
        )
        
    async def on_submit(self, interaction: nextcord.Interaction):
        """Default error-handled submit"""
        try:
            await self.handle_submit(interaction)
        except Exception as e:
            logger.error(f"Modal submit error: {e}")
            await interaction.response.send_message(
                "Ein Fehler ist aufgetreten",
                ephemeral=True
            )
            
    async def handle_submit(self, interaction: nextcord.Interaction):
        """Override this in subclasses"""
        raise NotImplementedError

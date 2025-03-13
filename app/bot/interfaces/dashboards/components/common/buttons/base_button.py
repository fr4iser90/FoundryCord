import nextcord
from typing import Optional, Callable, Coroutine
from app.shared.logging import logger

class BaseButton(nextcord.ui.Button):
    """Base class for all dashboard buttons"""
    
    def __init__(
        self,
        label: str,
        style: nextcord.ButtonStyle = nextcord.ButtonStyle.secondary,
        emoji: Optional[str] = None,
        custom_id: Optional[str] = None,
        row: Optional[int] = None,
        callback: Optional[Callable[[nextcord.Interaction], Coroutine]] = None
    ):
        super().__init__(
            label=label,
            style=style,
            emoji=emoji,
            custom_id=custom_id,
            row=row
        )
        if callback:
            self._callback = callback
            
    async def callback(self, interaction: nextcord.Interaction):
        """Default error-handled callback"""
        try:
            if hasattr(self, '_callback'):
                await self._callback(interaction)
            else:
                await self.default_callback(interaction)
        except Exception as e:
            logger.error(f"Button callback error: {e}")
            await interaction.response.send_message(
                "Ein Fehler ist aufgetreten", 
                ephemeral=True
            )
            
    async def default_callback(self, interaction: nextcord.Interaction):
        """Override this in subclasses"""
        await interaction.response.send_message(
            "Button nicht implementiert", 
            ephemeral=True
        )

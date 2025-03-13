import nextcord
from typing import Optional, Callable, Coroutine
from .base_button import BaseButton
from app.shared.logging import logger

class RefreshButton(BaseButton):
    """Standard refresh button implementation"""
    
    def __init__(
        self,
        callback: Optional[Callable[[nextcord.Interaction], Coroutine]] = None,
        label: str = "Aktualisieren",
        row: Optional[int] = None
    ):
        super().__init__(
            label=label,
            style=nextcord.ButtonStyle.secondary,
            emoji="🔄",
            custom_id="refresh_dashboard",
            row=row,
            callback=callback
        )
    
    async def default_callback(self, interaction: nextcord.Interaction):
        """Default refresh implementation"""
        try:
            await interaction.response.defer()
            await interaction.message.edit(content="Aktualisiere...", view=None)
            # Actual refresh logic should be injected via callback
            if not hasattr(self, '_callback'):
                await interaction.followup.send(
                    "Refresh-Handler nicht konfiguriert",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Refresh error: {e}")
            await interaction.followup.send(
                "Fehler beim Aktualisieren",
                ephemeral=True
            )

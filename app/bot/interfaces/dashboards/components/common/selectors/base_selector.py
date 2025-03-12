import nextcord
from typing import List, Optional, Callable, Any
from app.bot.infrastructure.logging import logger

class BaseSelector(nextcord.ui.Select):
    """Base class for all dashboard selectors"""
    
    def __init__(
        self,
        options: List[nextcord.SelectOption],
        placeholder: str = "Bitte wählen...",
        min_values: int = 1,
        max_values: int = 1,
        custom_id: Optional[str] = None,
        row: Optional[int] = None,
        callback: Optional[Callable[[nextcord.Interaction], Any]] = None
    ):
        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            custom_id=custom_id,
            row=row
        )
        self._callback = callback
        
    async def callback(self, interaction: nextcord.Interaction):
        """Default error-handled callback"""
        try:
            if self._callback:
                await self._callback(interaction)
            else:
                await self.default_callback(interaction)
        except Exception as e:
            logger.error(f"Selector callback error: {e}")
            await interaction.response.send_message(
                "Ein Fehler ist aufgetreten",
                ephemeral=True
            )
            
    async def default_callback(self, interaction: nextcord.Interaction):
        """Override this in subclasses"""
        await interaction.response.send_message(
            "Selector nicht implementiert",
            ephemeral=True
        ) 
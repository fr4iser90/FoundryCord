import nextcord
from infrastructure.logging import logger

class ConfirmationView(nextcord.ui.View):
    def __init__(self, title: str = "Bestätigung", timeout: int = 60):
        super().__init__(timeout=timeout)
        self.value = None
        self.title = title

    @nextcord.ui.button(label="Ja", style=nextcord.ButtonStyle.danger, emoji="✅")
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.defer()
        self.stop()

    @nextcord.ui.button(label="Nein", style=nextcord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.defer()
        self.stop()

    async def send_confirmation(self, interaction: nextcord.Interaction, message: str):
        """Sendet die Bestätigungsanfrage"""
        embed = nextcord.Embed(
            title=self.title,
            description=message,
            color=0xf44336
        )
        await interaction.response.send_message(embed=embed, view=self, ephemeral=True)

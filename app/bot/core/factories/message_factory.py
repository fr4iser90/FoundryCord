from typing import Optional, Dict, Any
import nextcord
from .base_factory import BaseFactory

class MessageFactory(BaseFactory):
    async def create_embed(self, 
        title: str, 
        description: str = None,
        color: int = 0x3498db,  # Discord Blau
        **kwargs
    ) -> nextcord.Embed:
        """Erstellt ein standardisiertes Embed"""
        embed = nextcord.Embed(
            title=title,
            description=description,
            color=color
        )
        if kwargs.get('footer'):
            embed.set_footer(text=kwargs['footer'])
        if kwargs.get('thumbnail'):
            embed.set_thumbnail(url=kwargs['thumbnail'])
        return embed

    async def create_error(self, message: str) -> nextcord.Embed:
        """Erstellt ein Error-Embed"""
        return await self.create_embed(
            title="❌ Error",
            description=message,
            color=0xe74c3c  # Rot
        )

    async def create_success(self, message: str) -> nextcord.Embed:
        """Erstellt ein Success-Embed"""
        return await self.create_embed(
            title="✅ Success",
            description=message,
            color=0x2ecc71  # Grün
        )

    async def create_warning(self, message: str) -> nextcord.Embed:
        """Erstellt ein Warning-Embed"""
        return await self.create_embed(
            title="⚠️ Warning",
            description=message,
            color=0xf1c40f  # Gelb
        )
from typing import Dict, Any
import nextcord
from app.bot.infrastructure.factories.base.base_factory import BaseFactory

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

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        embed = self.bot.loop.create_task(
            self.create_embed(
                title=kwargs.get('title', name),
                description=kwargs.get('description'),
                color=kwargs.get('color', 0x3498db),
                **kwargs
            )
        )
        return {
            'name': name,
            'embed': embed,
            'type': 'message',
            'config': kwargs
        }
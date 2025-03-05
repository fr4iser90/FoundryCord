from typing import Optional, Dict
from nextcord import CategoryChannel, TextChannel
import nextcord
from .base_factory import BaseFactory

class ChannelFactory(BaseFactory):
    def __init__(self, bot):
        super().__init__(bot)
        self._channels: Dict[str, TextChannel] = {}
        
    async def create_channel(self, 
            guild,
            name: str,
            category_id: Optional[int] = None,
            is_private: bool = False,
            topic: Optional[str] = None,
            slowmode: int = 0
        ) -> TextChannel:
        """Creates a channel with the given configuration"""
        category = self.bot.get_channel(category_id) if category_id else None
        
        channel_overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(
                read_messages=not is_private
            )
        }
        
        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=channel_overwrites,
            topic=topic,
            slowmode_delay=slowmode
        )
            
        self._channels[name] = channel
        return channel

    async def get_or_create_channel(self,
            guild,
            name: str,
            **kwargs
        ) -> TextChannel:
        """Gets existing channel or creates new one"""
        existing = self.get_channel(name)
        if existing:
            return existing
        return await self.create_channel(guild, name, **kwargs)

    def get_channel(self, name: str) -> Optional[TextChannel]:
        """Gets a channel by name"""
        return self._channels.get(name)
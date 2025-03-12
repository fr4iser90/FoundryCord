from typing import Optional, Dict, Any
from nextcord import CategoryChannel, TextChannel
import nextcord
from ..base.base_factory import BaseFactory
import logging

logger = logging.getLogger(__name__)

class ChannelFactory(BaseFactory):
    def __init__(self, bot):
        super().__init__(bot)
        self._channels: Dict[str, TextChannel] = {}
        
    async def create_channel(self, 
            guild,
            name: str,
            HOMELAB_CATEGORY_ID: Optional[int] = None,
            is_private: bool = False,
            topic: Optional[str] = None,
            slowmode: int = 0
        ) -> TextChannel:
        """Creates a channel with the given configuration"""
        # Kategorie aus Bot env_config holen
        category = self.bot.get_channel(self.bot.env_config.HOMELAB_CATEGORY_ID)
        if not category or not isinstance(category, CategoryChannel):
            logger.error(f"HOMELAB category not found or invalid! ID: {self.bot.env_config.HOMELAB_CATEGORY_ID}")
            return None

        # IN DER KATEGORIE nach existierendem Channel suchen
        existing_channel = nextcord.utils.get(category.channels, name=name)
        if existing_channel:
            logger.debug(f"Found existing channel '{name}' in HOMELAB category")
            self._channels[name] = existing_channel
            
            # WICHTIG: Auch für existierende Channels die ID speichern!
            from app.bot.infrastructure.config.channel_config import ChannelConfig
            await ChannelConfig.set_channel_id(name, existing_channel.id)
            
            return existing_channel
        
        channel_overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(
                read_messages=not is_private
            )
        }
        
        # Neuen Channel IN DER KATEGORIE erstellen
        channel = await guild.create_text_channel(
            name=name,
            category=category,  # Wichtig: Kategorie wird hier verwendet
            overwrites=channel_overwrites,
            topic=topic,
            slowmode_delay=slowmode
        )
            
        logger.info(f"Created new channel '{name}' in HOMELAB category")
        self._channels[name] = channel
        
        # Channel-ID in der Config speichern
        from app.bot.infrastructure.config.channel_config import ChannelConfig
        await ChannelConfig.set_channel_id(name, channel.id)
        
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

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        channel = self.bot.loop.create_task(
            self.get_or_create_channel(
                kwargs.get('guild'),
                name,
                is_private=kwargs.get('is_private', False),
                topic=kwargs.get('topic'),
                slowmode=kwargs.get('slowmode', 0)
            )
        )
        return {
            'name': name,
            'channel': channel,
            'type': 'channel',
            'config': kwargs
        }
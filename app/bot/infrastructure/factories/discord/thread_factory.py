from typing import Optional, Dict, Any
from nextcord import TextChannel, Thread
import nextcord
from ..base.base_factory import BaseFactory

class ThreadFactory(BaseFactory):
    def __init__(self, bot):
        super().__init__(bot)
        self._threads: Dict[str, Thread] = {}
        
    async def create_thread(self,
            channel: TextChannel,
            name: str,
            auto_archive_duration: int = 1440,
            is_private: bool = False,
            reason: Optional[str] = None
        ) -> Thread:
        """Creates a thread with the given configuration"""
        
        # Erst nach existierendem Thread suchen
        existing_thread = nextcord.utils.get(channel.threads, name=name)
        if existing_thread:
            thread_id = f"{channel.name}.{name}"
            self._threads[thread_id] = existing_thread
            
            # WICHTIG: Auch für existierende Threads die ID speichern!
            from infrastructure.config.channel_config import ChannelConfig
            await ChannelConfig.set_channel_id(thread_id, existing_thread.id)
            
            return existing_thread

        # Wenn nicht existiert, neu erstellen...
        thread = await channel.create_thread(
            name=name,
            auto_archive_duration=auto_archive_duration,
            type=nextcord.ChannelType.private_thread if is_private else nextcord.ChannelType.public_thread,
            reason=reason
        )
        
        thread_id = f"{channel.name}.{name}"
        self._threads[thread_id] = thread
        
        # Thread-ID in der Config speichern
        await ChannelConfig.set_channel_id(thread_id, thread.id)
        
        return thread
        
    async def get_or_create_thread(self,
            channel: TextChannel,
            name: str,
            **kwargs
        ) -> Thread:
        """Gets existing thread or creates new one"""
        # Prüfe zuerst in unserer lokalen Cache
        existing_thread = self.get_thread(channel, name)
        if existing_thread:
            if existing_thread.archived:
                await existing_thread.edit(archived=False)
            return existing_thread
        
        # Wenn nicht im Cache, suche in existierenden Threads des Channels
        for thread in channel.threads:
            if thread.name == name:
                # Thread gefunden, in Cache speichern
                thread_id = f"{channel.name}.{name}"
                self._threads[thread_id] = thread
                if thread.archived:
                    await thread.edit(archived=False)
                return thread
            
        # Wenn nicht gefunden, erstelle neuen Thread
        return await self.create_thread(channel, name, **kwargs)

    def get_thread(self, channel: TextChannel, thread_name: str) -> Optional[Thread]:
        """Gets a thread by channel name and thread name"""
        thread_id = f"{channel.name}.{thread_name}"  # Gleiche ID-Format wie in create_thread
        return self._threads.get(thread_id)

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        thread = self.bot.loop.create_task(
            self.get_or_create_thread(
                kwargs.get('channel'),
                name,
                auto_archive_duration=kwargs.get('auto_archive_duration', 1440),
                is_private=kwargs.get('is_private', False),
                reason=kwargs.get('reason')
            )
        )
        return {
            'name': name,
            'thread': thread,
            'type': 'thread',
            'config': kwargs
        }
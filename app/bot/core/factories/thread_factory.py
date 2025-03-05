from typing import Optional, Dict, Any
from nextcord import TextChannel, Thread
import nextcord
from .base_factory import BaseFactory

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
        thread = await channel.create_thread(
            name=name,
            auto_archive_duration=auto_archive_duration,
            type=nextcord.ChannelType.private_thread if is_private else nextcord.ChannelType.public_thread,
            reason=reason
        )
        
        self._threads[f"{channel.id}_{name}"] = thread
        return thread
        
    async def get_or_create_thread(self,
            channel: TextChannel,
            name: str,
            **kwargs
        ) -> Thread:
        """Gets existing thread or creates new one"""
        existing_thread = self.get_thread(channel.id, name)
        if existing_thread:
            if existing_thread.archived:
                await existing_thread.edit(archived=False)
            return existing_thread
            
        return await self.create_thread(channel, name, **kwargs)

    def get_thread(self, channel_id: int, thread_name: str) -> Optional[Thread]:
        """Gets a thread by channel ID and thread name"""
        return self._threads.get(f"{channel_id}_{thread_name}")

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
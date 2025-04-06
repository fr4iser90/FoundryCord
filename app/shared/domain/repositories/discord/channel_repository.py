from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity
from app.shared.infrastructure.models.discord.mappings.channel_mapping import ChannelMapping

class ChannelRepository(ABC):
    """Interface for Channel repository operations"""
    
    @abstractmethod
    def get_all_channels(self) -> List[ChannelEntity]:
        """Get all channels from the database"""
        pass
    
    @abstractmethod
    def get_channel_by_id(self, channel_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its database ID"""
        pass
    
    @abstractmethod
    def get_channel_by_discord_id(self, discord_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its Discord ID"""
        pass
    
    @abstractmethod
    def get_channel_by_name_and_category(self, name: str, category_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its name and category ID"""
        pass
    
    @abstractmethod
    def get_channels_by_category_id(self, category_id: int) -> List[ChannelEntity]:
        """Get all channels in a specific category"""
        pass
    
    @abstractmethod
    def get_channels_by_category_discord_id(self, category_discord_id: int) -> List[ChannelEntity]:
        """Get all channels in a specific Discord category"""
        pass
    
    @abstractmethod
    def save_channel(self, channel: ChannelEntity) -> ChannelEntity:
        """Save a channel to the database (create or update)"""
        pass
    
    @abstractmethod
    def update_discord_id(self, channel_id: int, discord_id: int) -> bool:
        """Update the Discord ID of a channel after it's created in Discord"""
        pass
    
    @abstractmethod
    def update_channel_status(self, channel_id: int, is_created: bool) -> bool:
        """Update the creation status of a channel"""
        pass
    
    @abstractmethod
    def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel from the database"""
        pass
    
    @abstractmethod
    def create_from_template(self, template: ChannelEntity, category_id: Optional[int] = None, 
                           category_discord_id: Optional[int] = None) -> ChannelEntity:
        """Create a new channel from a template"""
        pass
    
    @abstractmethod
    def get_enabled_channels(self) -> List[ChannelEntity]:
        """Get all enabled channels"""
        pass
    
    @abstractmethod
    def get_channels_by_type(self, channel_type: str) -> List[ChannelEntity]:
        """Get all channels of a specific type"""
        pass
    
    @abstractmethod
    def get_channel_mapping(self) -> Dict[str, ChannelMapping]:
        """Get a mapping of channel names to channel mappings"""
        pass 
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class ChannelType(Enum):
    """Types of Discord channels"""
    TEXT = "text"
    VOICE = "voice"
    FORUM = "forum"
    ANNOUNCEMENT = "announcement"
    STAGE = "stage"


class ChannelPermissionLevel(Enum):
    """Permission levels for channels in Discord"""
    PUBLIC = "public"
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class ChannelPermission:
    """Represents permissions for a specific role within a channel"""
    role_id: int
    view: bool = False
    send_messages: bool = False
    read_messages: bool = False
    manage_messages: bool = False
    manage_channel: bool = False
    use_bots: bool = False
    embed_links: bool = False
    attach_files: bool = False
    add_reactions: bool = False


@dataclass
class ThreadConfig:
    """Configuration for forum or text channel thread settings"""
    default_auto_archive_duration: int = 1440  # In minutes (1 day)
    default_thread_slowmode_delay: int = 0  # In seconds
    default_reaction_emoji: Optional[str] = None
    require_tag: bool = False
    available_tags: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.available_tags is None:
            self.available_tags = []


@dataclass
class ChannelModel:
    """Domain model representing a Discord channel"""
    id: Optional[int] = None  # Database ID
    discord_id: Optional[int] = None  # Discord channel ID
    name: str = ""
    description: Optional[str] = None
    category_id: Optional[int] = None  # Database category ID
    category_discord_id: Optional[int] = None  # Discord category ID
    type: ChannelType = ChannelType.TEXT
    position: int = 0
    permission_level: ChannelPermissionLevel = ChannelPermissionLevel.PUBLIC
    permissions: List[ChannelPermission] = None
    is_enabled: bool = True
    is_created: bool = False
    nsfw: bool = False
    slowmode_delay: int = 0  # In seconds
    topic: Optional[str] = None
    thread_config: Optional[ThreadConfig] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.metadata is None:
            self.metadata = {}
        if self.type in [ChannelType.FORUM, ChannelType.TEXT] and self.thread_config is None:
            self.thread_config = ThreadConfig()
    
    @property
    def is_valid(self) -> bool:
        """Validate if channel has all required information"""
        # A channel is valid if it has a name, and either:
        # - is attached to a category (has category_id or category_discord_id)
        # - or is a top-level channel (for special cases)
        return bool(self.name and (self.category_id is not None or self.category_discord_id is not None))


@dataclass
class ChannelTemplate:
    """Template for creating channels with predefined configurations"""
    name: str
    description: Optional[str]
    category_name: str  # Reference to category by name
    type: ChannelType
    position: int
    permission_level: ChannelPermissionLevel
    permissions: List[ChannelPermission]
    nsfw: bool = False
    slowmode_delay: int = 0
    topic: Optional[str] = None
    thread_config: Optional[ThreadConfig] = None
    metadata: Dict[str, Any] = None
    is_enabled: bool = True
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.type in [ChannelType.FORUM, ChannelType.TEXT] and self.thread_config is None:
            self.thread_config = ThreadConfig()
    
    def to_channel_model(self, category_id: Optional[int] = None, category_discord_id: Optional[int] = None) -> ChannelModel:
        """Convert template to a ChannelModel instance"""
        return ChannelModel(
            name=self.name,
            description=self.description,
            category_id=category_id,
            category_discord_id=category_discord_id,
            type=self.type,
            position=self.position,
            permission_level=self.permission_level,
            permissions=self.permissions.copy() if self.permissions else [],
            nsfw=self.nsfw,
            slowmode_delay=self.slowmode_delay,
            topic=self.topic,
            thread_config=self.thread_config,
            metadata=self.metadata.copy() if self.metadata else {},
            is_enabled=self.is_enabled
        ) 
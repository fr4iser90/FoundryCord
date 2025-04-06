from enum import Enum

class ChannelType(Enum):
    """Types of Discord channels"""
    TEXT = "text"
    VOICE = "voice"
    CATEGORY = "category"
    NEWS = "news"
    STORE = "store"
    FORUM = "forum"
    THREAD = "thread"

class ChannelPermissionLevel(Enum):
    """Permission levels for channels"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    ADMIN = "admin"

class CategoryPermissionLevel(Enum):
    """Permission levels for categories"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    ADMIN = "admin" 
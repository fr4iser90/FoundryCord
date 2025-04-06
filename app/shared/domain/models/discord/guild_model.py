from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

class GuildAccessStatus(Enum):
    """Status of guild access"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    BLOCKED = "BLOCKED"

@dataclass
class GuildModel:
    """Domain model for Discord guilds"""
    guild_id: str
    name: str
    icon_url: Optional[str] = None
    owner_id: Optional[str] = None
    member_count: int = 0
    joined_at: datetime = None
    settings: Dict[str, Any] = None
    is_active: bool = True
    access_status: GuildAccessStatus = GuildAccessStatus.PENDING
    access_requested_at: datetime = None
    access_reviewed_at: Optional[datetime] = None
    access_reviewed_by: Optional[str] = None
    access_notes: Optional[str] = None
    enable_commands: bool = False
    enable_logging: bool = True
    enable_automod: bool = False
    enable_welcome: bool = False 
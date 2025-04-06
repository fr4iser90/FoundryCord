from enum import Enum

class MessageType(Enum):
    """Types of messages"""
    TEXT = "text"
    EMBED = "embed"
    SYSTEM = "system"
    WELCOME = "welcome"
    GOODBYE = "goodbye"
    ANNOUNCEMENT = "announcement"
    NOTIFICATION = "notification"

class MessageStatus(Enum):
    """Status of messages"""
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed" 
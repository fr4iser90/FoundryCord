from enum import Enum

class GuildAccessStatus(Enum):
    """Access status for guilds"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class GuildFeatureFlag(Enum):
    """Feature flags for guilds"""
    COMMANDS = "commands"
    LOGGING = "logging"
    AUTOMOD = "automod"
    WELCOME = "welcome"
    CATEGORIES = "categories"
    CHANNELS = "channels"
    DASHBOARD = "dashboard"
    TASKS = "tasks"
    SERVICES = "services" 
"""
Constants related to Discord categories used by the Homelab bot.
This defines the structure and properties of categories.
"""

CATEGORIES = {
    'homelab': {
        'name': 'Homelab',
        'description': 'Main category for homelab management',
        'is_private': True,
        'position': 0
    },
    'gameservers': {
        'name': 'Homelab Game Servers',
        'description': 'Category for game servers and related channels',
        'is_private': False,
        'position': 1
    }
}

# Category to channel mappings - defines which channels should be created in which category
CATEGORY_CHANNEL_MAPPINGS = {
    'homelab': [
        'welcome',
        'services',
        'gamehub',
        'infrastructure',
        'projects',
        'backups',
        'server-management',
        'logs',
        'monitoring',
        'bot-control',
        'alerts'
    ],
    'gameservers': [
        ''
    ]
}

# Default category (used when no specific category is defined)
DEFAULT_CATEGORY = 'homelab'

# Flag constants for category features
ENABLE_HOMELAB_CATEGORY = True
ENABLE_GAMESERVERS_CATEGORY = True

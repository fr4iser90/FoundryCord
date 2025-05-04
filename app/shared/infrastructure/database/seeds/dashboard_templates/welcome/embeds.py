"""Embed definitions for welcome dashboard migration"""
from typing import Dict, Any

WELCOME_EMBEDS = {
    "welcome_main_embed": {
        "title": "Welcome to HomeLab Discord",
        "description": "This server is dedicated to managing and monitoring homelab systems.",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Rules",
                "value": "Please read and accept our server rules to gain access to all channels.",
                "inline": False
            },
            {
                "name": "Getting Started",
                "value": "Select your interests below to gain access to relevant channels.",
                "inline": False
            },
            {
                "name": "Need Help?",
                "value": "Click the Help button below or ask in the #support channel.",
                "inline": False
            }
        ],
        "footer": {
            "text": "HomeLab Bot - Making your homelab experience better"
        }
    },
    "server_info_embed": {
        "title": "Server Information",
        "description": "Details about this Discord server",
        "color": 0x2ecc71,
        "fields": [
            {
                "name": "Purpose",
                "value": "This server is designed to help with homelab management, monitoring, and project collaboration.",
                "inline": False
            },
            {
                "name": "Features",
                "value": "• System monitoring\n• Project management\n• Game server management\n• Technical support\n• Resource sharing",
                "inline": False
            }
        ]
    },
    "bot_info_embed": {
        "title": "HomeLab Bot Information",
        "description": "All about the HomeLab Discord Bot",
        "color": 0xe74c3c,
        "fields": [
            {
                "name": "Purpose",
                "value": "This bot provides monitoring, management, and automation for your homelab.",
                "inline": False
            },
            {
                "name": "Commands",
                "value": "Type `/help` to see available commands",
                "inline": False
            },
            {
                "name": "Features",
                "value": "• System monitoring\n• Docker container management\n• Game server control\n• Project tracking\n• Resource utilization",
                "inline": False
            },
            {
                "name": "GitHub",
                "value": "[View Source Code](https://github.com/yourusername/discord-server-bot)",
                "inline": False
            }
        ]
    }
}

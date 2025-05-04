"""Button definitions for welcome dashboard migration"""
from typing import Dict, List, Any

WELCOME_BUTTONS = {
    "accept_rules_button": {
        "label": "Accept Rules",
        "style": "success",
        "emoji": "✅",
        "custom_id": "welcome_accept_rules",
        "row": 0
    },
    "server_info_button": {
        "label": "Server Info",
        "style": "primary",
        "emoji": "ℹ️",
        "custom_id": "welcome_server_info",
        "row": 0
    },
    "bot_info_button": {
        "label": "Bot Info",
        "style": "secondary",
        "emoji": "🤖",
        "custom_id": "welcome_bot_info",
        "row": 0
    },
    "close_button": {
        "label": "Close",
        "style": "danger",
        "emoji": "❌",
        "custom_id": "welcome_close",
        "row": 1
    },
    "help_button": {
        "label": "Help",
        "style": "secondary",
        "emoji": "❓",
        "custom_id": "welcome_help",
        "row": 1
    }
}

"""Button definitions for common dashboard migration"""
from typing import Dict, List, Any

# This is likely still defined as a list, not a dictionary
DEFAULT_BUTTONS = {
    "back_button": {
        "label": "Back",
        "style": "secondary",
        "emoji": "◀️",
        "custom_id": "common_back",
        "row": 0
    },
    "home_button": {
        "label": "Home",
        "style": "secondary",
        "emoji": "🏠",
        "custom_id": "common_home",
        "row": 0
    },
    "help_button": {
        "label": "Help",
        "style": "secondary",
        "emoji": "❓",
        "custom_id": "common_help",
        "row": 0
    },
    "cancel_button": {
        "label": "Cancel",
        "style": "danger",
        "emoji": "❌",
        "custom_id": "common_cancel",
        "row": 1
    },
    "confirm_button": {
        "label": "Confirm",
        "style": "success",
        "emoji": "✅",
        "custom_id": "common_confirm",
        "row": 1
    }
}

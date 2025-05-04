"""View definitions for welcome dashboard migration"""
from typing import Dict, Any

WELCOME_VIEWS = {
    "welcome_view": {
        "timeout": None,
        "buttons": [
            "accept_rules_button",
            "server_info_button",
            "bot_info_button"
        ],
        "selectors": [
            "tech_selector"
        ]
    },
    "bot_info_view": {
        "timeout": 300,
        "buttons": [
            "close_button",
            "help_button"
        ]
    },
    "server_info_view": {
        "timeout": 300,
        "buttons": [
            "close_button"
        ]
    }
}

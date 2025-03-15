"""Default view definitions for dashboard migration"""
from typing import Dict, Any

DEFAULT_VIEWS = {
    "confirmation_view": {
        "timeout": 60,  # 1 minute timeout
        "buttons": [
            "confirm_button",
            "cancel_button"
        ]
    },
    "pagination_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "back_button",
            "next_button",
            "close_button" 
        ]
    },
    "detail_view": {
        "timeout": 180,  # 3 minute timeout
        "buttons": [
            "back_button",
            "refresh_button"
        ]
    },
    "help_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "close_button"
        ]
    }
}

"""Default embed definitions for dashboard migration"""
from typing import Dict, Any

DEFAULT_EMBEDS = {
    "error_embed": {
        "title": "❌ Error",
        "description": "An error occurred while processing your request.",
        "color": 0xe74c3c,  # Red
        "fields": [
            {
                "name": "Error Details",
                "value": "{{error_message}}"
            }
        ]
    },
    "success_embed": {
        "title": "✅ Success",
        "description": "Operation completed successfully!",
        "color": 0x2ecc71  # Green
    },
    "warning_embed": {
        "title": "⚠️ Warning",
        "description": "{{warning_message}}",
        "color": 0xf39c12  # Yellow/Orange
    },
    "info_embed": {
        "title": "ℹ️ Information",
        "description": "{{info_message}}",
        "color": 0x3498db  # Blue
    },
    "confirmation_embed": {
        "title": "🔍 Confirmation Required",
        "description": "Are you sure you want to proceed with this action?",
        "color": 0x9b59b6,  # Purple
        "fields": [
            {
                "name": "Action",
                "value": "{{action_description}}"
            }
        ]
    },
    "loading_embed": {
        "title": "⏳ Loading",
        "description": "Please wait while the operation completes...",
        "color": 0x95a5a6  # Gray
    }
}

"""Default embed definitions for dashboard migration"""
from typing import Dict, Any

DEFAULT_EMBEDS = {
    "error": {
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
    "success": {
        "title": "✅ Success",
        "description": "Operation completed successfully!",
        "color": 0x2ecc71  # Green
    },
    "warning": {
        "title": "⚠️ Warning",
        "description": "{{warning_message}}",
        "color": 0xf39c12  # Yellow/Orange
    },
    "info": {
        "title": "ℹ️ Information",
        "description": "{{info_message}}",
        "color": 0x3498db  # Blue
    },
    "confirmation": {
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
    "loading": {
        "title": "⏳ Loading",
        "description": "Please wait while the operation completes...",
        "color": 0x95a5a6  # Gray
    }
}

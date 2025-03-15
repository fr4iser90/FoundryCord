"""Selector definitions for gamehub dashboard migration"""
from typing import Dict, List, Any

GAMEHUB_SELECTORS = {
    "server_action_selector": {
        "placeholder": "Select Action",
        "custom_id": "server_action_select",
        "options": [
            {
                "label": "Start Server",
                "value": "start",
                "emoji": "▶️",
                "description": "Start the server"
            },
            {
                "label": "Stop Server",
                "value": "stop",
                "emoji": "⏹️",
                "description": "Stop the server"
            },
            {
                "label": "Restart Server",
                "value": "restart",
                "emoji": "🔄",
                "description": "Restart the server"
            },
            {
                "label": "Backup World",
                "value": "backup",
                "emoji": "💾",
                "description": "Create a backup of the world"
            },
            {
                "label": "View Logs",
                "value": "logs",
                "emoji": "📜",
                "description": "View server logs"
            }
        ]
    },
    "server_filter_selector": {
        "placeholder": "Filter Servers",
        "custom_id": "server_filter_select",
        "options": [
            {
                "label": "All Servers",
                "value": "all",
                "emoji": "🎮",
                "description": "Show all game servers"
            },
            {
                "label": "Running Servers",
                "value": "running",
                "emoji": "✅",
                "description": "Show only running servers"
            },
            {
                "label": "Stopped Servers",
                "value": "stopped",
                "emoji": "⛔",
                "description": "Show only stopped servers"
            }
        ]
    }
}

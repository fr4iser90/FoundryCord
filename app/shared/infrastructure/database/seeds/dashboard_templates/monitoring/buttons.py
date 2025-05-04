"""Button definitions for monitoring dashboard migration"""
from typing import Dict, List, Any

MONITORING_BUTTONS = {
    "system_details_button": {
        "label": "System",
        "style": "primary",
        "emoji": "🖥️",
        "custom_id": "system_details",
        "row": 0
    },
    "cpu_details_button": {
        "label": "CPU",
        "style": "primary",
        "emoji": "📊",
        "custom_id": "cpu_details",
        "row": 0
    },
    "memory_details_button": {
        "label": "Memory",
        "style": "primary",
        "emoji": "🧠",
        "custom_id": "memory_details",
        "row": 0
    },
    "disk_details_button": {
        "label": "Disk",
        "style": "primary",
        "emoji": "💾",
        "custom_id": "disk_details",
        "row": 0
    },
    "network_details_button": {
        "label": "Network",
        "style": "primary",
        "emoji": "🌐",
        "custom_id": "network_details",
        "row": 1
    },
    "processes_button": {
        "label": "Processes",
        "style": "primary",
        "emoji": "📝",
        "custom_id": "processes",
        "row": 1
    },
    "docker_services_button": {
        "label": "Services",
        "style": "primary",
        "emoji": "🐳",
        "custom_id": "docker_services",
        "row": 1
    },
    "game_servers_button": {
        "label": "Games",
        "style": "primary", 
        "emoji": "🎮",
        "custom_id": "game_servers",
        "row": 1
    },
    "view_logs_button": {
        "label": "Logs",
        "style": "secondary",
        "emoji": "📜",
        "custom_id": "view_logs",
        "row": 1
    },
    "refresh_button": {
        "label": "Refresh",
        "style": "secondary",
        "emoji": "🔄",
        "custom_id": "refresh_monitoring",
        "row": 0
    }
}

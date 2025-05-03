"""Button definitions for monitoring dashboard migration"""
from typing import Dict, List, Any

MONITORING_BUTTONS = {
    "system_details": {
        "label": "System",
        "style": "primary",
        "emoji": "🖥️",
        "custom_id": "system_details",
        "row": 0
    },
    "cpu_details": {
        "label": "CPU",
        "style": "primary",
        "emoji": "📊",
        "custom_id": "cpu_details",
        "row": 0
    },
    "memory_details": {
        "label": "Memory",
        "style": "primary",
        "emoji": "🧠",
        "custom_id": "memory_details",
        "row": 0
    },
    "disk_details": {
        "label": "Disk",
        "style": "primary",
        "emoji": "💾",
        "custom_id": "disk_details",
        "row": 0
    },
    "network_details": {
        "label": "Network",
        "style": "primary",
        "emoji": "🌐",
        "custom_id": "network_details",
        "row": 1
    },
    "processes": {
        "label": "Processes",
        "style": "primary",
        "emoji": "📝",
        "custom_id": "processes",
        "row": 1
    },
    "docker_services": {
        "label": "Services",
        "style": "primary",
        "emoji": "🐳",
        "custom_id": "docker_services",
        "row": 1
    },
    "game_servers": {
        "label": "Games",
        "style": "primary", 
        "emoji": "🎮",
        "custom_id": "game_servers",
        "row": 1
    },
    "view_logs": {
        "label": "Logs",
        "style": "secondary",
        "emoji": "📜",
        "custom_id": "view_logs",
        "row": 1
    },
    "refresh": {
        "label": "Refresh",
        "style": "secondary",
        "emoji": "🔄",
        "custom_id": "refresh_monitoring",
        "row": 0
    }
}

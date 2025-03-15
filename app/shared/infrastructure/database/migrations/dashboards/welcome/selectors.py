"""Selector definitions for welcome dashboard migration"""
from typing import Dict, List, Any

WELCOME_SELECTORS = {
    "tech_selector": {
        "placeholder": "Select Your Interests",
        "custom_id": "tech_interests",
        "min_values": 1,
        "max_values": 5,
        "options": [
            {
                "label": "System Monitoring",
                "value": "monitoring",
                "emoji": "📊",
                "description": "Server and system monitoring tools"
            },
            {
                "label": "Docker",
                "value": "docker",
                "emoji": "🐳",
                "description": "Container management and orchestration"
            },
            {
                "label": "Game Servers",
                "value": "games",
                "emoji": "🎮",
                "description": "Setting up and managing game servers"
            },
            {
                "label": "Networking",
                "value": "networking",
                "emoji": "🌐",
                "description": "Network infrastructure and management"
            },
            {
                "label": "Storage",
                "value": "storage",
                "emoji": "💾",
                "description": "NAS, SAN, and data storage solutions"
            },
            {
                "label": "Hardware",
                "value": "hardware",
                "emoji": "🔧",
                "description": "Server hardware and components"
            },
            {
                "label": "Programming",
                "value": "programming",
                "emoji": "💻",
                "description": "Development and coding"
            }
        ]
    }
}

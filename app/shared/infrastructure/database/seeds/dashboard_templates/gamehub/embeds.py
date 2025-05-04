"""Embed definitions for gamehub dashboard migration"""
from typing import Dict, List, Any

GAMEHUB_EMBEDS = {
    "gamehub_main_embed": {
        "title": "🎮 Game Server Dashboard",
        "description": "View and manage all available game servers.",
        "color": 0x2ecc71,
        "fields": [
            {
                "name": "Available Servers",
                "value": "Click on a server button to view details and manage the server."
            },
            {
                "name": "Server Status",
                "value": "{{server_status_summary}}"
            }
        ]
    },
    "minecraft_server_embed": {
        "title": "⛏️ Minecraft Server",
        "description": "Minecraft server status and management",
        "color": 0x4f8a10,
        "fields": [
            {
                "name": "Status",
                "value": "{{status}}",
                "inline": True
            },
            {
                "name": "Players",
                "value": "{{current_players}}/{{max_players}}",
                "inline": True
            },
            {
                "name": "Version",
                "value": "{{version}}",
                "inline": True
            },
            {
                "name": "Uptime",
                "value": "{{uptime}}",
                "inline": True
            },
            {
                "name": "IP Address",
                "value": "{{server_ip}}",
                "inline": True
            },
            {
                "name": "CPU Usage",
                "value": "{{cpu_usage}}%",
                "inline": True
            },
            {
                "name": "Memory Usage",
                "value": "{{memory_usage}} MB",
                "inline": True
            }
        ]
    },
    "factorio_server_embed": {
        "title": "🏭 Factorio Server",
        "description": "Factorio server status and management",
        "color": 0xf79e11,
        "fields": [
            {
                "name": "Status",
                "value": "{{status}}",
                "inline": True
            },
            {
                "name": "Players",
                "value": "{{current_players}}/{{max_players}}",
                "inline": True
            },
            {
                "name": "Version",
                "value": "{{version}}",
                "inline": True
            },
            {
                "name": "Save",
                "value": "{{save_name}}",
                "inline": True
            },
            {
                "name": "Uptime",
                "value": "{{uptime}}",
                "inline": True
            },
            {
                "name": "Mods",
                "value": "{{mod_count}} installed",
                "inline": True
            }
        ]
    }
}

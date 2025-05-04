"""Button definitions for gamehub dashboard migration"""
from typing import Dict, List, Any

GAMEHUB_BUTTONS = {
    "minecraft_server_button": {
        "label": "Minecraft",
        "style": "primary",
        "emoji": "⛏️",
        "custom_id": "game_minecraft",
        "row": 0
    },
    "factorio_server_button": {
        "label": "Factorio",
        "style": "primary",
        "emoji": "🏭",
        "custom_id": "game_factorio",
        "row": 0
    },
    "valheim_server_button": {
        "label": "Valheim",
        "style": "primary",
        "emoji": "⚔️",
        "custom_id": "game_valheim",
        "row": 0
    },
    "terraria_server_button": {
        "label": "Terraria",
        "style": "primary",
        "emoji": "🌳",
        "custom_id": "game_terraria",
        "row": 1
    },
    "satisfactory_server_button": {
        "label": "Satisfactory",
        "style": "primary",
        "emoji": "🏗️",
        "custom_id": "game_satisfactory",
        "row": 1
    },
    "ark_server_button": {
        "label": "ARK",
        "style": "primary",
        "emoji": "🦖",
        "custom_id": "game_ark",
        "row": 1
    },
    "refresh_servers_button": {
        "label": "Refresh",
        "style": "secondary",
        "emoji": "🔄",
        "custom_id": "refresh_gameservers",
        "row": 2
    },
    "add_server_button": {
        "label": "Add Server",
        "style": "success",
        "emoji": "➕",
        "custom_id": "add_gameserver",
        "row": 2
    }
}

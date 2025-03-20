"""Button definitions for gamehub dashboard migration"""
from typing import Dict, List, Any

GAMEHUB_BUTTONS = {
    "minecraft_server": {
        "label": "Minecraft",
        "style": "primary",
        "emoji": "⛏️",
        "custom_id": "game_minecraft",
        "row": 0
    },
    "factorio_server": {
        "label": "Factorio",
        "style": "primary",
        "emoji": "🏭",
        "custom_id": "game_factorio",
        "row": 0
    },
    "valheim_server": {
        "label": "Valheim",
        "style": "primary",
        "emoji": "⚔️",
        "custom_id": "game_valheim",
        "row": 0
    },
    "terraria_server": {
        "label": "Terraria",
        "style": "primary",
        "emoji": "🌳",
        "custom_id": "game_terraria",
        "row": 1
    },
    "satisfactory_server": {
        "label": "Satisfactory",
        "style": "primary",
        "emoji": "🏗️",
        "custom_id": "game_satisfactory",
        "row": 1
    },
    "ark_server": {
        "label": "ARK",
        "style": "primary",
        "emoji": "🦖",
        "custom_id": "game_ark",
        "row": 1
    },
    "refresh_servers": {
        "label": "Refresh",
        "style": "secondary",
        "emoji": "🔄",
        "custom_id": "refresh_gameservers",
        "row": 2
    },
    "add_server": {
        "label": "Add Server",
        "style": "success",
        "emoji": "➕",
        "custom_id": "add_gameserver",
        "row": 2
    }
}

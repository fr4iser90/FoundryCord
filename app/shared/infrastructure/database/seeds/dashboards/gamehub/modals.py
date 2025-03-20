"""Modal definitions for gamehub dashboard migration"""
from typing import Dict, List, Any

GAMEHUB_MODALS = {
    "add_server_modal": {
        "title": "Add Game Server",
        "fields": [
            {
                "name": "game_type",
                "label": "Game Type",
                "placeholder": "minecraft, factorio, valheim, etc.",
                "required": True,
                "min_length": 1,
                "max_length": 50
            },
            {
                "name": "server_name",
                "label": "Server Name",
                "placeholder": "A unique name for this server",
                "required": True,
                "min_length": 1,
                "max_length": 50
            },
            {
                "name": "server_address",
                "label": "Server Address",
                "placeholder": "IP address or hostname",
                "required": True
            },
            {
                "name": "server_port",
                "label": "Server Port",
                "placeholder": "Port number",
                "required": True
            },
            {
                "name": "description",
                "label": "Description",
                "placeholder": "Optional description of this server",
                "style": "paragraph",
                "required": False
            }
        ]
    },
    "server_command_modal": {
        "title": "Run Server Command",
        "fields": [
            {
                "name": "command",
                "label": "Server Command",
                "placeholder": "Enter command to run on the server",
                "required": True,
                "min_length": 1,
                "max_length": 100
            }
        ]
    }
}

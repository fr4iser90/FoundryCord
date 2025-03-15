"""View definitions for gamehub dashboard migration"""
from typing import Dict, Any

GAMEHUB_VIEWS = {
    "gamehub_view": {
        "timeout": None,
        "buttons": [
            "minecraft_server",
            "factorio_server",
            "valheim_server",
            "terraria_server",
            "satisfactory_server", 
            "ark_server",
            "refresh_servers",
            "add_server"
        ],
        "selectors": [
            "server_filter_selector"
        ],
        "auto_refresh": 300  # Auto refresh every 5 minutes
    },
    "server_detail_view": {
        "timeout": 300,  # 5 minutes
        "buttons": [
            "refresh_servers"
        ],
        "selectors": [
            "server_action_selector"
        ]
    }
}

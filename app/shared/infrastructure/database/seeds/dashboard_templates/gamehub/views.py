"""View definitions for gamehub dashboard migration"""
from typing import Dict, Any

GAMEHUB_VIEWS = {
    "gamehub_view": {
        "timeout": None,
        "buttons": [
            "minecraft_server_button",
            "factorio_server_button",
            "valheim_server_button",
            "terraria_server_button",
            "satisfactory_server_button", 
            "ark_server_button",
            "refresh_servers_button",
            "add_server_button"
        ],
        "selectors": [
            "server_filter_selector"
        ],
        "auto_refresh": 300  # Auto refresh every 5 minutes
    },
    "server_detail_view": {
        "timeout": 300,  # 5 minutes
        "buttons": [
            "refresh_servers_button"
        ],
        "selectors": [
            "server_action_selector"
        ]
    }
}

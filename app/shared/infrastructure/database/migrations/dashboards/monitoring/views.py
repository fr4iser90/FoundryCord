"""View definitions for monitoring dashboard migration"""
from typing import Dict, Any

MONITORING_VIEWS = {
    "monitoring_view": {
        "timeout": None,
        "buttons": [
            "system_details",
            "cpu_details",
            "memory_details", 
            "disk_details",
            "network_details",
            "processes",
            "docker_services",
            "game_servers",
            "view_logs",
            "refresh"
        ],
        "auto_refresh": 300  # Auto refresh every 5 minutes
    },
    "detail_view": {
        "timeout": 180,  # Close after 3 minutes of inactivity
        "buttons": ["back_to_overview", "refresh"]
    }
}

"""View definitions for monitoring dashboard migration"""
from typing import Dict, Any

MONITORING_VIEWS = {
    "monitoring_view": {
        "timeout": None,
        "buttons": [
            "system_details_button",
            "cpu_details_button",
            "memory_details_button", 
            "disk_details_button",
            "network_details_button",
            "processes_button",
            "docker_services_button",
            "game_servers_button",
            "view_logs_button",
            "refresh_button"
        ],
        "auto_refresh": 300  # Auto refresh every 5 minutes
    },
    "detail_view": {
        "timeout": 180,  # Close after 3 minutes of inactivity
        "buttons": ["back_to_overview_button", "refresh_button"]
    }
}

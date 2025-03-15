"""Modal definitions for monitoring dashboard migration"""
from typing import Dict, List, Any

MONITORING_MODALS = {
    "command_modal": {
        "title": "Run Command",
        "fields": [
            {
                "name": "command",
                "label": "Command",
                "placeholder": "Enter command to run",
                "required": True,
                "min_length": 1,
                "max_length": 100
            },
            {
                "name": "args",
                "label": "Arguments",
                "placeholder": "Command arguments (optional)",
                "required": False
            }
        ]
    }
}

"""Message definitions for monitoring dashboard migration"""
from typing import Dict, Any

MONITORING_MESSAGES = {
    "error_message": {
        "title": "Error Fetching Data",
        "description": "Unable to retrieve system metrics. Please try again later.",
        "color": 0xe74c3c
    },
    "success_message": {
        "title": "Command Executed",
        "description": "The command was executed successfully.",
        "color": 0x2ecc71
    },
    "loading_message": {
        "title": "Loading Data",
        "description": "Retrieving system metrics...",
        "color": 0x3498db
    }
}

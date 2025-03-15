"""Message definitions for gamehub dashboard migration"""
from typing import Dict, Any

GAMEHUB_MESSAGES = {
    "server_started": {
        "content": "Server started successfully!",
        "ephemeral": True
    },
    "server_stopped": {
        "content": "Server stopped successfully!",
        "ephemeral": True
    },
    "server_restarted": {
        "content": "Server restarted successfully!",
        "ephemeral": True
    },
    "server_not_found": {
        "content": "Server not found or not properly configured.",
        "ephemeral": True
    },
    "operation_failed": {
        "content": "Failed to perform the requested operation. Check logs for details.",
        "ephemeral": True
    },
    "operation_in_progress": {
        "content": "Operation in progress, please wait...",
        "ephemeral": True
    }
}

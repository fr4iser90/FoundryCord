"""Message definitions for gamehub dashboard migration"""
from typing import Dict, Any

GAMEHUB_MESSAGES = {
    "server_started_message": {
        "content": "Server started successfully!",
        "ephemeral": True
    },
    "server_stopped_message": {
        "content": "Server stopped successfully!",
        "ephemeral": True
    },
    "server_restarted_message": {
        "content": "Server restarted successfully!",
        "ephemeral": True
    },
    "server_not_found_message": {
        "content": "Server not found or not properly configured.",
        "ephemeral": True
    },
    "operation_failed_message": {
        "content": "Failed to perform the requested operation. Check logs for details.",
        "ephemeral": True
    },
    "operation_in_progress_message": {
        "content": "Operation in progress, please wait...",
        "ephemeral": True
    }
}

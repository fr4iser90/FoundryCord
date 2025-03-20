"""Default message definitions for dashboard migration"""
from typing import Dict, Any

DEFAULT_MESSAGES = {
    "error": {
        "content": "An error occurred: {{error_message}}",
        "ephemeral": True
    },
    "success": {
        "content": "Operation completed successfully!",
        "ephemeral": True
    },
    "warning": {
        "content": "Warning: {{warning_message}}",
        "ephemeral": True
    },
    "info": {
        "content": "{{info_message}}",
        "ephemeral": True
    },
    "not_authorized": {
        "content": "You don't have permission to perform this action.",
        "ephemeral": True
    },
    "timeout": {
        "content": "The operation timed out. Please try again.",
        "ephemeral": True
    },
    "confirmation": {
        "content": "Are you sure you want to perform this action?",
        "ephemeral": True
    },
    "rate_limited": {
        "content": "You're doing that too often. Please wait before trying again.",
        "ephemeral": True
    }
}

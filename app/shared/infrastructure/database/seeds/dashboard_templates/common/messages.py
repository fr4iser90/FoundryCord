"""Default message definitions for dashboard migration"""
from typing import Dict, Any

DEFAULT_MESSAGES = {
    "error_message": {
        "content": "An error occurred: {{error_message}}",
        "ephemeral": True
    },
    "success_message": {
        "content": "Operation completed successfully!",
        "ephemeral": True
    },
    "warning_message": {
        "content": "Warning: {{warning_message}}",
        "ephemeral": True
    },
    "info_message": {
        "content": "{{info_message}}",
        "ephemeral": True
    },
    "not_authorized_message": {
        "content": "You don't have permission to perform this action.",
        "ephemeral": True
    },
    "timeout_message": {
        "content": "The operation timed out. Please try again.",
        "ephemeral": True
    },
    "confirmation_message": {
        "content": "Are you sure you want to perform this action?",
        "ephemeral": True
    },
    "rate_limited_message": {
        "content": "You're doing that too often. Please wait before trying again.",
        "ephemeral": True
    }
}

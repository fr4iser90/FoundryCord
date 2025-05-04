"""Message definitions for welcome dashboard migration"""
from typing import Dict, Any

WELCOME_MESSAGES = {
    "welcome_message": {
        "content": "Welcome to the HomeLab Discord server! Please check out the information below.",
        "ephemeral": False
    },
    "rules_accepted_message": {
        "content": "Thank you for accepting the rules! You now have access to all channels.",
        "ephemeral": True
    },
    "already_accepted_message": {
        "content": "You have already accepted the rules.",
        "ephemeral": True
    },
    "error_message": {
        "content": "An error occurred. Please try again or contact an administrator.",
        "ephemeral": True
    }
}

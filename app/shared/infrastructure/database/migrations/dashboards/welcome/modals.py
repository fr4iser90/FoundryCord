"""Modal definitions for welcome dashboard migration"""
from typing import Dict, List, Any

WELCOME_MODALS = {
    "introduction_modal": {
        "title": "Introduce Yourself",
        "fields": [
            {
                "name": "name",
                "label": "Name/Nickname",
                "placeholder": "What should we call you?",
                "required": True,
                "min_length": 1,
                "max_length": 50
            },
            {
                "name": "experience",
                "label": "Homelab Experience",
                "placeholder": "Tell us a bit about your homelab experience",
                "style": "paragraph",
                "required": False
            },
            {
                "name": "interests",
                "label": "Areas of Interest",
                "placeholder": "What homelab topics are you interested in?",
                "style": "paragraph",
                "required": False
            }
        ]
    },
    "feedback_modal": {
        "title": "Server Feedback",
        "fields": [
            {
                "name": "feedback",
                "label": "Your Feedback",
                "placeholder": "Please share your thoughts about the server",
                "style": "paragraph",
                "required": True
            },
            {
                "name": "suggestions",
                "label": "Suggestions",
                "placeholder": "Any ideas for improvements?",
                "style": "paragraph",
                "required": False
            }
        ]
    }
}

"""Default modal definitions for dashboard migration"""
from typing import Dict, List, Any

DEFAULT_MODALS = {
    "text_input_modal": {
        "title": "Enter Information",
        "fields": [
            {
                "name": "text_input",
                "label": "Input",
                "placeholder": "Enter your text here...",
                "required": True,
                "min_length": 1,
                "max_length": 100
            }
        ]
    },
    "confirmation_modal": {
        "title": "Confirm Action",
        "fields": [
            {
                "name": "confirmation",
                "label": "Type 'confirm' to proceed",
                "placeholder": "confirm",
                "required": True,
                "min_length": 7,
                "max_length": 7
            }
        ]
    },
    "feedback_modal": {
        "title": "Submit Feedback",
        "fields": [
            {
                "name": "feedback_type",
                "label": "Feedback Type",
                "placeholder": "Bug report, suggestion, general feedback",
                "required": True,
                "min_length": 2,
                "max_length": 50
            },
            {
                "name": "feedback_content",
                "label": "Your Feedback",
                "placeholder": "Please provide details about your feedback...",
                "required": True,
                "style": "paragraph",
                "min_length": 10,
                "max_length": 1000
            }
        ]
    }
}

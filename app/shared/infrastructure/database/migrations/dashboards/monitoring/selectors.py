"""Selector definitions for monitoring dashboard migration"""
from typing import Dict, List, Any

MONITORING_SELECTORS = {
    "timeframe_selector": {
        "placeholder": "Select Timeframe",
        "custom_id": "timeframe_select",
        "options": [
            {
                "label": "Last Hour",
                "value": "1h",
                "emoji": "⏱️",
                "description": "Show data from the last hour"
            },
            {
                "label": "Last 6 Hours",
                "value": "6h",
                "emoji": "⏱️",
                "description": "Show data from the last 6 hours"
            },
            {
                "label": "Last 24 Hours",
                "value": "24h",
                "emoji": "⏱️",
                "description": "Show data from the last 24 hours"
            },
            {
                "label": "Last 7 Days",
                "value": "7d",
                "emoji": "📅",
                "description": "Show data from the last 7 days"
            }
        ]
    },
    "service_selector": {
        "placeholder": "Select Service",
        "custom_id": "service_select",
        "options": [
            {
                "label": "All Services",
                "value": "all",
                "emoji": "🔍",
                "description": "Show all services"
            },
            {
                "label": "Web Services",
                "value": "web",
                "emoji": "🌐",
                "description": "Show web services only"
            },
            {
                "label": "Database Services",
                "value": "db",
                "emoji": "🗄️",
                "description": "Show database services only"
            },
            {
                "label": "System Services",
                "value": "system",
                "emoji": "⚙️",
                "description": "Show system services only"
            }
        ]
    }
}

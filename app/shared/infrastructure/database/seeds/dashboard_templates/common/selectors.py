"""Default selector definitions for dashboard migration"""
from typing import Dict, List, Any

DEFAULT_SELECTORS = {
    "sort_selector": {
        "placeholder": "Sort By",
        "custom_id": "sort_select",
        "options": [
            {
                "label": "Name (A-Z)",
                "value": "name_asc",
                "emoji": "🔤",
                "description": "Sort alphabetically"
            },
            {
                "label": "Name (Z-A)",
                "value": "name_desc",
                "emoji": "🔤",
                "description": "Sort reverse alphabetically"
            },
            {
                "label": "Date (Newest)",
                "value": "date_desc",
                "emoji": "📅",
                "description": "Sort by newest first"
            },
            {
                "label": "Date (Oldest)",
                "value": "date_asc",
                "emoji": "📅",
                "description": "Sort by oldest first"
            }
        ]
    },
    "filter_selector": {
        "placeholder": "Filter Items",
        "custom_id": "filter_select",
        "options": [
            {
                "label": "All Items",
                "value": "all",
                "emoji": "🔍",
                "description": "Show all items"
            },
            {
                "label": "Active Only",
                "value": "active",
                "emoji": "✅",
                "description": "Show only active items"
            },
            {
                "label": "Inactive Only",
                "value": "inactive",
                "emoji": "❌",
                "description": "Show only inactive items"
            }
        ]
    },
    "page_size_selector": {
        "placeholder": "Items Per Page",
        "custom_id": "page_size_select",
        "options": [
            {
                "label": "5 Items",
                "value": "5",
                "emoji": "5️⃣",
                "description": "Show 5 items per page"
            },
            {
                "label": "10 Items",
                "value": "10",
                "emoji": "🔟",
                "description": "Show 10 items per page"
            },
            {
                "label": "25 Items",
                "value": "25",
                "emoji": "📋",
                "description": "Show 25 items per page" 
            }
        ]
    }
}

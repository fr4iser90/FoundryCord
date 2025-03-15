"""Button definitions for project dashboard migration"""
from typing import Dict, List, Any

PROJECT_BUTTONS = {
    "create_project": {
        "label": "New Project",
        "style": "success",
        "emoji": "➕",
        "custom_id": "create_project",
        "row": 0
    },
    "view_projects": {
        "label": "View All",
        "style": "primary",
        "emoji": "📋",
        "custom_id": "view_projects",
        "row": 0
    },
    "my_projects": {
        "label": "My Projects",
        "style": "primary",
        "emoji": "👤",
        "custom_id": "my_projects",
        "row": 0
    },
    "active_projects": {
        "label": "Active",
        "style": "primary",
        "emoji": "✅",
        "custom_id": "active_projects",
        "row": 1
    },
    "completed_projects": {
        "label": "Completed",
        "style": "secondary",
        "emoji": "🏁",
        "custom_id": "completed_projects",
        "row": 1
    },
    "edit_project": {
        "label": "Edit",
        "style": "primary",
        "emoji": "✏️",
        "custom_id": "edit_project",
        "row": 2
    },
    "delete_project": {
        "label": "Delete",
        "style": "danger",
        "emoji": "🗑️",
        "custom_id": "delete_project",
        "row": 2
    },
    "project_details": {
        "label": "Details",
        "style": "secondary",
        "emoji": "🔍",
        "custom_id": "project_details",
        "row": 2
    },
    "add_task": {
        "label": "Add Task",
        "style": "success",
        "emoji": "📝",
        "custom_id": "add_task",
        "row": 3
    },
    "refresh_projects": {
        "label": "Refresh",
        "style": "secondary",
        "emoji": "🔄",
        "custom_id": "refresh_projects",
        "row": 3
    }
}
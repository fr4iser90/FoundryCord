"""Selector definitions for project dashboard migration"""
from typing import Dict, List, Any

PROJECT_SELECTORS = {
    "project_filter_selector": {
        "placeholder": "Filter Projects",
        "custom_id": "project_filter_select",
        "options": [
            {
                "label": "All Projects",
                "value": "all",
                "emoji": "📋",
                "description": "Show all projects"
            },
            {
                "label": "Active Projects",
                "value": "active",
                "emoji": "✅",
                "description": "Show only active projects"
            },
            {
                "label": "Completed Projects",
                "value": "completed",
                "emoji": "🏁",
                "description": "Show only completed projects"
            },
            {
                "label": "My Projects",
                "value": "my",
                "emoji": "👤",
                "description": "Show only your projects"
            },
            {
                "label": "High Priority",
                "value": "high_priority",
                "emoji": "🔴",
                "description": "Show high priority projects"
            }
        ]
    },
    "project_sort_selector": {
        "placeholder": "Sort Projects",
        "custom_id": "project_sort_select",
        "options": [
            {
                "label": "Latest First",
                "value": "date_desc",
                "emoji": "📅",
                "description": "Sort by newest first"
            },
            {
                "label": "Oldest First",
                "value": "date_asc",
                "emoji": "📅",
                "description": "Sort by oldest first"
            },
            {
                "label": "Name (A-Z)",
                "value": "name_asc",
                "emoji": "🔤",
                "description": "Sort alphabetically"
            },
            {
                "label": "Deadline (Nearest)",
                "value": "deadline_asc",
                "emoji": "⏰",
                "description": "Sort by nearest deadline"
            },
            {
                "label": "Priority (Highest)",
                "value": "priority_desc",
                "emoji": "⚠️",
                "description": "Sort by highest priority first"
            }
        ]
    },
    "team_member_selector": {
        "placeholder": "Add Team Member",
        "custom_id": "team_member_select",
        "options": [
            {
                "label": "{{username}}",
                "value": "{{user_id}}",
                "description": "Add {{username}} to the project"
            }
        ]
    },
    "task_status_selector": {
        "placeholder": "Update Task Status",
        "custom_id": "task_status_select",
        "options": [
            {
                "label": "Not Started",
                "value": "not_started",
                "emoji": "⭕",
                "description": "Task not yet started"
            },
            {
                "label": "In Progress",
                "value": "in_progress",
                "emoji": "🔄",
                "description": "Task is in progress"
            },
            {
                "label": "Completed",
                "value": "completed",
                "emoji": "✅",
                "description": "Task is completed"
            },
            {
                "label": "Blocked",
                "value": "blocked",
                "emoji": "🚫",
                "description": "Task is blocked"
            }
        ]
    }
}

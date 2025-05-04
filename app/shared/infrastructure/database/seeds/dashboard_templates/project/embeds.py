"""Embed definitions for project dashboard migration"""
from typing import Dict, Any

PROJECT_EMBEDS = {
    "project_dashboard_embed": {
        "title": "📊 Project Dashboard",
        "description": "Manage and track your projects from one place.",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Active Projects",
                "value": "{{active_project_count}} active projects",
                "inline": True
            },
            {
                "name": "Completed Projects",
                "value": "{{completed_project_count}} completed projects",
                "inline": True
            },
            {
                "name": "My Projects",
                "value": "{{my_project_count}} assigned to you",
                "inline": True
            }
        ]
    },
    "project_list_embed": {
        "title": "📋 Project List",
        "description": "All available projects",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Projects",
                "value": "{{projects}}",
                "inline": False
            }
        ]
    },
    "project_details_embed": {
        "title": "🔍 {{project_name}}",
        "description": "{{project_description}}",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Status",
                "value": "{{project_status}}",
                "inline": True
            },
            {
                "name": "Owner",
                "value": "{{project_owner}}",
                "inline": True
            },
            {
                "name": "Created",
                "value": "{{created_date}}",
                "inline": True
            },
            {
                "name": "Deadline",
                "value": "{{deadline}}",
                "inline": True
            },
            {
                "name": "Progress",
                "value": "{{progress}}% complete",
                "inline": True
            },
            {
                "name": "Priority",
                "value": "{{priority}}",
                "inline": True
            },
            {
                "name": "Tasks",
                "value": "{{task_list}}",
                "inline": False
            },
            {
                "name": "Team Members",
                "value": "{{team_members}}",
                "inline": False
            }
        ]
    },
    "task_list_embed": {
        "title": "📝 Tasks for {{project_name}}",
        "description": "Manage tasks for this project",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Tasks",
                "value": "{{task_list}}",
                "inline": False
            }
        ]
    }
}
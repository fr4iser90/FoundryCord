"""Embed definitions for project dashboard migration"""
from typing import Dict, Any

PROJECT_EMBEDS = {
    "project_dashboard": {
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
    "project_list": {
        "title": "📋 Project List",
        "description": "All available projects",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Projects",
                "value": "{{project_list}}",
                "inline": False
            }
        ]
    },
    "project_details": {
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
    "task_list": {
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
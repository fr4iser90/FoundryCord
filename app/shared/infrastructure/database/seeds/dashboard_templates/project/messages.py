"""Message definitions for project dashboard migration"""
from typing import Dict, Any

PROJECT_MESSAGES = {
    "project_created_message": {
        "content": "Project has been created successfully!",
        "ephemeral": True
    },
    "project_updated_message": {
        "content": "Project has been updated successfully!",
        "ephemeral": True
    },
    "project_deleted_message": {
        "content": "Project has been deleted successfully!",
        "ephemeral": True
    },
    "task_added_message": {
        "content": "Task has been added to the project!",
        "ephemeral": True
    },
    "task_completed_message": {
        "content": "Task marked as completed!",
        "ephemeral": True
    },
    "member_added_message": {
        "content": "Team member added to the project!",
        "ephemeral": True
    },
    "no_projects_message": {
        "content": "No projects found. Create a new project to get started!",
        "ephemeral": True
    },
    "project_not_found_message": {
        "content": "Project not found. It may have been deleted.",
        "ephemeral": True
    },
    "unauthorized_message": {
        "content": "You don't have permission to modify this project.",
        "ephemeral": True
    }
}

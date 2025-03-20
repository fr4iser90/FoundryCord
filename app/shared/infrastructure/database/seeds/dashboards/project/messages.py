"""Message definitions for project dashboard migration"""
from typing import Dict, Any

PROJECT_MESSAGES = {
    "project_created": {
        "content": "Project has been created successfully!",
        "ephemeral": True
    },
    "project_updated": {
        "content": "Project has been updated successfully!",
        "ephemeral": True
    },
    "project_deleted": {
        "content": "Project has been deleted successfully!",
        "ephemeral": True
    },
    "task_added": {
        "content": "Task has been added to the project!",
        "ephemeral": True
    },
    "task_completed": {
        "content": "Task marked as completed!",
        "ephemeral": True
    },
    "member_added": {
        "content": "Team member added to the project!",
        "ephemeral": True
    },
    "no_projects": {
        "content": "No projects found. Create a new project to get started!",
        "ephemeral": True
    },
    "project_not_found": {
        "content": "Project not found. It may have been deleted.",
        "ephemeral": True
    },
    "unauthorized": {
        "content": "You don't have permission to modify this project.",
        "ephemeral": True
    }
}

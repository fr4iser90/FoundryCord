"""Modal definitions for project dashboard migration"""
from typing import Dict, List, Any

PROJECT_MODALS = {
    "create_project_modal": {
        "title": "Create New Project",
        "fields": [
            {
                "name": "name",
                "label": "Project Name",
                "placeholder": "Enter project name",
                "required": True,
                "min_length": 3,
                "max_length": 100
            },
            {
                "name": "description",
                "label": "Description",
                "placeholder": "Enter project description",
                "required": True,
                "style": "paragraph",
                "min_length": 10,
                "max_length": 1000
            },
            {
                "name": "deadline",
                "label": "Deadline (YYYY-MM-DD)",
                "placeholder": "YYYY-MM-DD",
                "required": False
            },
            {
                "name": "priority",
                "label": "Priority (Low, Medium, High)",
                "placeholder": "Medium",
                "required": False
            }
        ]
    },
    "edit_project_modal": {
        "title": "Edit Project",
        "fields": [
            {
                "name": "name",
                "label": "Project Name",
                "placeholder": "Enter project name",
                "required": True,
                "min_length": 3,
                "max_length": 100
            },
            {
                "name": "description",
                "label": "Description",
                "placeholder": "Enter project description",
                "required": True,
                "style": "paragraph",
                "min_length": 10,
                "max_length": 1000
            },
            {
                "name": "deadline",
                "label": "Deadline (YYYY-MM-DD)",
                "placeholder": "YYYY-MM-DD",
                "required": False
            },
            {
                "name": "status",
                "label": "Status",
                "placeholder": "Active, On Hold, Completed",
                "required": False
            }
        ]
    },
    "add_task_modal": {
        "title": "Add Task",
        "fields": [
            {
                "name": "task_name",
                "label": "Task Name",
                "placeholder": "Enter task name",
                "required": True,
                "min_length": 3,
                "max_length": 100
            },
            {
                "name": "task_description",
                "label": "Description",
                "placeholder": "Enter task description",
                "style": "paragraph",
                "required": False
            },
            {
                "name": "assignee",
                "label": "Assignee",
                "placeholder": "Enter the username of assignee",
                "required": False
            },
            {
                "name": "due_date",
                "label": "Due Date (YYYY-MM-DD)",
                "placeholder": "YYYY-MM-DD",
                "required": False
            }
        ]
    }
}

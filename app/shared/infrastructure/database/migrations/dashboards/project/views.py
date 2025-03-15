"""View definitions for project dashboard migration"""
from typing import Dict, Any

PROJECT_VIEWS = {
    "project_dashboard_view": {
        "timeout": None,  # No timeout for main dashboard
        "buttons": [
            "create_project",
            "view_projects",
            "my_projects",
            "active_projects",
            "completed_projects",
            "refresh_projects"
        ],
        "selectors": [
            "project_filter_selector",
            "project_sort_selector"
        ]
    },
    "project_detail_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "edit_project",
            "delete_project",
            "add_task",
            "back_button",
            "refresh_projects"
        ],
        "selectors": [
            "task_status_selector",
            "team_member_selector"
        ]
    },
    "project_list_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "create_project",
            "refresh_projects",
            "back_button"
        ],
        "selectors": [
            "project_sort_selector"
        ]
    },
    "task_management_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "add_task",
            "back_button"
        ],
        "selectors": [
            "task_status_selector"
        ]
    }
}

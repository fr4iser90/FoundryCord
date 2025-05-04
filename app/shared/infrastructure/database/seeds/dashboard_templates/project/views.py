"""View definitions for project dashboard migration"""
from typing import Dict, Any

PROJECT_VIEWS = {
    "project_dashboard_view": {
        "timeout": None,  # No timeout for main dashboard
        "buttons": [
            "create_project_button",
            "view_projects_button",
            "my_projects_button",
            "active_projects_button",
            "completed_projects_button",
            "refresh_projects_button"
        ],
        "selectors": [
            "project_filter_selector",
            "project_sort_selector"
        ]
    },
    "project_detail_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "edit_project_button",
            "delete_project_button",
            "add_task_button",
            "back_button",
            "refresh_projects_button"
        ],
        "selectors": [
            "task_status_selector",
            "team_member_selector"
        ]
    },
    "project_list_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "create_project_button",
            "refresh_projects_button",
            "back_button"
        ],
        "selectors": [
            "project_sort_selector"
        ]
    },
    "task_management_view": {
        "timeout": 300,  # 5 minute timeout
        "buttons": [
            "add_task_button",
            "back_button"
        ],
        "selectors": [
            "task_status_selector"
        ]
    }
}

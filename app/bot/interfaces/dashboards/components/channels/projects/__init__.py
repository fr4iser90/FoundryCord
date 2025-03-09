# Import from old locations but expose via new structure
from .buttons.project_buttons import ProjectActionButtons as ProjectButtons
from .buttons.project_task_buttons import TaskActionButtons as TaskButtons
from .modals.project_modal import ProjectModal
from .modals.project_task_modal import TaskModal
from .views.project_dashboard_view import ProjectDashboardView
from .views.project_details_view import ProjectDetailsView
from .views.project_task_list_view import TaskListView
from .views.project_thread_view import ProjectThreadView
from .views.status_select_view import StatusSelectView

__all__ = [
    'ProjectButtons',
    'TaskButtons',
    'ProjectModal',
    'TaskModal',
    'ProjectDashboardView',
    'ProjectDetailsView',
    'TaskListView',
    'ProjectThreadView',
    'StatusSelectView'
]
from .dashboard_controller import DashboardController, dashboard_controller

router = dashboard_controller.router

__all__ = ['DashboardController', 'router'] 
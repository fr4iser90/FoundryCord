from .dashboard_controller import dashboard_controller

# Assign the controller's router to the module-level router variable
router = dashboard_controller.router

# Define the public interface for this module
__all__ = ['router'] 
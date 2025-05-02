from .debug_controller import debug_controller

# Assign the controller's router to the module-level router variable
router = debug_controller.router

# Define the public interface for this module
__all__ = ['router'] 
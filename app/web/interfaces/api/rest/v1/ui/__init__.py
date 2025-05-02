from .layout_controller import layout_controller

# Assign the controller's router to the module-level router variable
router = layout_controller.router

# Define the public interface for this module
__all__ = ['router'] 
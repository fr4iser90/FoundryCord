from .auth_controller import auth_controller

# Assign the controller's router to the module-level router variable
router = auth_controller.router

# Define the public interface for this module
__all__ = ['router'] 
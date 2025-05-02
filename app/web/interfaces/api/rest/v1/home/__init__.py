# Import the router instance directly from the overview controller module
from .overview_controller import router as overview_router

# Assign the imported router to the module-level 'router' variable
router = overview_router

# Define the public interface for this module
__all__ = ['router'] 
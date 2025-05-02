from fastapi import APIRouter

from .dashboard_controller import dashboard_controller
# Import the component controller
from .dashboard_component_controller import dashboard_component_controller

# Create a new router for the dashboards module
router = APIRouter()

# Include routers from both controllers
router.include_router(dashboard_controller.router)
router.include_router(dashboard_component_controller.router)

# Define the public interface for this module
__all__ = ['router'] 
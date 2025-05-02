from fastapi import APIRouter

# Import controller instances to access their routers
from .metadata_controller import metadata_controller
from .structure_controller import structure_controller
from .lifecycle_controller import lifecycle_controller

# Create a router for the designer sub-module
router = APIRouter()

# Include the routers from the individual controllers
router.include_router(metadata_controller.router)
router.include_router(structure_controller.router)
router.include_router(lifecycle_controller.router)

# Define the public interface for this module
__all__ = ['router'] 
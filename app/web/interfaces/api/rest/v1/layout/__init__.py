from fastapi import APIRouter
from .layout_controller import LayoutController, layout_controller
# Create a router for the guild module
router = APIRouter()

# Include routes from all guild-related controllers
router.include_router(layout_controller.router)

__all__ = [
    'LayoutController', 
    'layout_controller', 
    'router' # Export the combined router
] 
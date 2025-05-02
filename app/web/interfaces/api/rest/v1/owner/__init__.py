from fastapi import APIRouter

# Import individual controller instances
from .owner_controller import owner_controller
from .bot_control_controller import bot_control_controller
from .guild_management_controller import guild_management_controller
from .bot_logger_controller import bot_logger_controller
from .state_snapshot_controller import state_snapshot_controller

# Create an aggregating router for the owner section
router = APIRouter()

# Include the routers from each controller
router.include_router(owner_controller.router)
router.include_router(bot_control_controller.router)
router.include_router(guild_management_controller.router)
router.include_router(bot_logger_controller.router)
router.include_router(state_snapshot_controller.router)

# Define the public interface for this module
__all__ = ['router']
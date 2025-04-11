# Import the router instance directly from the refactored module
from .overview_controller import router as home_overview_router

# Export the router so it can be included in the main API router
__all__ = [
    'home_overview_router' # Renamed export for clarity
] 
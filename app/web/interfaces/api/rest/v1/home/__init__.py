# Import the router instance directly from the module
from .overview_controller import router

overview_controller_router = router # Use a name reflecting the source


__all__ = [
    'overview_controller_router', 
    'router' 
] 
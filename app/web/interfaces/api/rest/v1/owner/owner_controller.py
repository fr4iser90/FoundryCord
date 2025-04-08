from fastapi import APIRouter
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()
router = APIRouter(prefix="/owner", tags=["Owner Controls"])

class OwnerController:
    """Controller for owner-specific functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        pass  # Add routes as needed

# Create controller instance
owner_controller = OwnerController()
    

from fastapi import APIRouter
from app.web.interfaces.web.views import routers as view_routers

# Create a master router for all web routes
router = APIRouter()

# Include all web view routers
for view_router in view_routers:
    router.include_router(view_router) 
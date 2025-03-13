from fastapi import APIRouter
from app.web.interfaces.api.v1 import routers as v1_routers

# Create a master router for all API routes
router = APIRouter(prefix="/api", tags=["API"])

# Include v1 API routers
for api_router in v1_routers:
    router.include_router(api_router)

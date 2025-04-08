from fastapi import APIRouter
from app.web.interfaces.api.rest.v1 import routers as v1_routers

router = APIRouter()
# Include all web view routers
for api_router in v1_routers:
    router.include_router(api_router)

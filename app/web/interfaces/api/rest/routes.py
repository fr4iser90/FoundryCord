from fastapi import APIRouter
from app.web.interfaces.api.rest.v1 import router as v1_router

router = APIRouter()
router.include_router(v1_router)

__all__ = ['router']

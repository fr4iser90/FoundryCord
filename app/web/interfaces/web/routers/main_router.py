from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.interfaces.web.dependencies import get_templates
from app.web.domain.auth.dependencies import get_current_user
from app.web.infrastructure.database.repositories import SQLAlchemyDashboardRepository
from app.shared.infrastructure.database.core.connection import get_db_connection
from .auth_router import router as auth_router
from .dashboard_router import router as dashboard_router
from .admin_router import router as admin_router

router = APIRouter()
templates = get_templates()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user=Depends(get_current_user)):
    """Main index page"""
    # Temporär: Keine Dashboards laden bis Repository implementiert ist
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": current_user, "dashboards": []}
    )

# Include all routers
router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(admin_router)

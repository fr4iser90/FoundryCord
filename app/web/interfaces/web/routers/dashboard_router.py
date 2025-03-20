from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.web.interfaces.web.dependencies import get_templates
from app.web.domain.auth.dependencies import get_current_user
from app.web.infrastructure.database.repositories import SQLAlchemyDashboardRepository
from app.shared.infrastructure.database.core.connection import get_db_connection

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])
templates = get_templates()

@router.get("/", response_class=HTMLResponse)
async def list_dashboards(request: Request, current_user=Depends(get_current_user)):
    """List all dashboards"""
    db = await get_db_connection()
    repo = SQLAlchemyDashboardRepository(db)
    dashboards = await repo.get_all()
    return templates.TemplateResponse(
        "pages/dashboards/view.html",
        {"request": request, "dashboards": dashboards, "user": current_user}
    )

@router.get("/builder", response_class=HTMLResponse)
async def dashboard_builder(request: Request, current_user=Depends(get_current_user)):
    """Dashboard builder interface"""
    return templates.TemplateResponse(
        "pages/dashboards/builder.html",
        {"request": request, "user": current_user}
    )

@router.get("/templates", response_class=HTMLResponse)
async def dashboard_templates(request: Request, current_user=Depends(get_current_user)):
    """Dashboard templates library"""
    return templates.TemplateResponse(
        "pages/dashboards/templates.html",
        {"request": request, "user": current_user}
    )

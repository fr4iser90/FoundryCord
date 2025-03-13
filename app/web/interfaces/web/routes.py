from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import os
import pathlib
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.domain.auth.dependencies import get_current_user
from app.web.domain.dashboard_builder.models import Dashboard
from app.web.application.services.dashboard import DashboardService
from app.web.infrastructure.database.repositories import SQLAlchemyDashboardRepository
from app.web.infrastructure.database.connection import get_db_session

router = APIRouter(tags=["Web UI"])

# Get templates directory
base_dir = pathlib.Path(__file__).parent.parent.parent
templates_dir = os.path.join(base_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Get dashboard service
async def get_dashboard_service(session: AsyncSession = Depends(get_db_session)):
    repository = SQLAlchemyDashboardRepository(session)
    return DashboardService(repository)

@router.get("/dashboard/builder", response_class=HTMLResponse)
async def dashboard_builder(
    request: Request,
    id: str = None,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(get_current_user)
):
    """Dashboard builder page"""
    if not current_user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "message": "Please login to access the dashboard builder"}
        )
    
    dashboard = None
    if id:
        dashboard = await service.get_dashboard(id)
        if not dashboard or dashboard.user_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    
    return templates.TemplateResponse("dashboard_builder.html", {"request": request, "user": current_user, "dashboard": dashboard})

@router.get("/dashboard/view/{dashboard_id}", response_class=HTMLResponse)
async def dashboard_view(
    request: Request,
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(get_current_user)
):
    """Dashboard viewer page"""
    dashboard = await service.get_dashboard(dashboard_id)
    
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
        
    # Check permissions - public dashboards can be viewed by anyone
    if not dashboard.is_public and (not current_user or dashboard.user_id != current_user["id"]):
        if not current_user:
            return templates.TemplateResponse(
                "login.html", 
                {"request": request, "message": "Please login to view this dashboard"}
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to view this dashboard")
    
    # Convert dashboard to JSON for the template
    dashboard_json = dashboard.json()
    
    return templates.TemplateResponse(
        "dashboard_view.html", 
        {
            "request": request, 
            "user": current_user, 
            "dashboard": dashboard,
            "dashboard_json": dashboard_json
        }
    )

@router.get("/dashboards", response_class=HTMLResponse)
async def dashboards_list(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(get_current_user)
):
    """Dashboards list page"""
    if not current_user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "message": "Please login to view your dashboards"}
        )
    
    dashboards = await service.get_user_dashboards(current_user["id"])
    
    return templates.TemplateResponse(
        "dashboards.html", 
        {"request": request, "user": current_user, "dashboards": dashboards}
    )

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    # If authentication fails, user will be None
    dashboards = []
    if current_user:
        # Create service with the provided session
        service = DashboardService(SQLAlchemyDashboardRepository(session))
        dashboards = await service.get_user_dashboards(current_user["id"])
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "user": current_user, "dashboards": dashboards}
    ) 
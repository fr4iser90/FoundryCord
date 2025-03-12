from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..services.auth_service import get_current_user
from ..services.dashboard_service import DashboardService
from ..models.user import User
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
import logging
import json

router = APIRouter()
logger = logging.getLogger("web_interface.dashboard")
templates = Jinja2Templates(directory="app/bot/interfaces/web/templates")

@router.get("/")
async def list_dashboards(
    request: Request, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all dashboards for the user
    """
    dashboard_service = DashboardService(db)
    dashboards = await dashboard_service.get_dashboards_by_user(current_user.id)
    
    return templates.TemplateResponse(
        "dashboard_list.html", 
        {
            "request": request,
            "user": current_user,
            "dashboards": dashboards
        }
    )

@router.get("/create")
async def create_dashboard_form(
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    """
    Show dashboard creation form
    """
    return templates.TemplateResponse(
        "dashboard_create.html", 
        {
            "request": request,
            "user": current_user
        }
    )

@router.post("/create")
async def create_dashboard(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    dashboard_type: str = Form(...),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new dashboard
    """
    try:
        dashboard_service = DashboardService(db)
        
        # Create initial empty layout
        layout = {
            "grid": {
                "columns": 12,
                "rows": 12
            },
            "components": []
        }
        
        # Create dashboard
        dashboard = await dashboard_service.create_dashboard(
            user_id=current_user.id,
            title=title,
            description=description,
            dashboard_type=dashboard_type,
            layout=json.dumps(layout),
            is_public=is_public
        )
        
        return RedirectResponse(
            url=f"/dashboard/{dashboard.id}/edit",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        logger.error(f"Error creating dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dashboard"
        )

@router.get("/{dashboard_id}")
async def view_dashboard(
    request: Request,
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View a dashboard
    """
    dashboard_service = DashboardService(db)
    dashboard = await dashboard_service.get_dashboard_by_id(dashboard_id)
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check if user has access
    if dashboard.user_id != current_user.id and not dashboard.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this dashboard"
        )
    
    # Parse layout
    layout = json.loads(dashboard.layout)
    
    return templates.TemplateResponse(
        "dashboard_view.html", 
        {
            "request": request,
            "user": current_user,
            "dashboard": dashboard,
            "layout": layout
        }
    )

@router.get("/{dashboard_id}/edit")
async def edit_dashboard_form(
    request: Request,
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Show dashboard edit form
    """
    dashboard_service = DashboardService(db)
    dashboard = await dashboard_service.get_dashboard_by_id(dashboard_id)
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Check if user is the owner
    if dashboard.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this dashboard"
        )
    
    # Parse layout
    layout = json.loads(dashboard.layout)
    
    return templates.TemplateResponse(
        "dashboard_edit.html", 
        {
            "request": request,
            "user": current_user,
            "dashboard": dashboard,
            "layout": layout
        }
    )

@router.post("/{dashboard_id}/edit")
async def update_dashboard(
    request: Request,
    dashboard_id: int,
    title: str = Form(...),
    description: str = Form(None),
    is_public: bool = Form(False),
    layout_json: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a dashboard
    """
    try:
        dashboard_service = DashboardService(db)
        dashboard = await dashboard_service.get_dashboard_by_id(dashboard_id)
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Check if user is the owner
        if dashboard.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this dashboard"
            )
        
        # Validate layout JSON
        try:
            layout = json.loads(layout_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid layout JSON"
            )
        
        # Update dashboard
        await dashboard_service.update_dashboard(
            dashboard_id=dashboard_id,
            title=title,
            description=description,
            layout=layout_json,
            is_public=is_public
        )
        
        return RedirectResponse(
            url=f"/dashboard/{dashboard_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dashboard"
        )

@router.post("/{dashboard_id}/delete")
async def delete_dashboard(
    request: Request,
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a dashboard
    """
    try:
        dashboard_service = DashboardService(db)
        dashboard = await dashboard_service.get_dashboard_by_id(dashboard_id)
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Check if user is the owner
        if dashboard.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this dashboard"
            )
        
        # Delete dashboard
        await dashboard_service.delete_dashboard(dashboard_id)
        
        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dashboard"
        ) 
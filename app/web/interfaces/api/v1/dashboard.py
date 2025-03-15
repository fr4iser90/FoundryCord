from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.web.domain.auth.dependencies import get_current_user, require_moderator
from app.web.domain.dashboard_builder.models import Dashboard, DashboardCreate, DashboardUpdate, Widget, WidgetCreate
from app.web.application.services.dashboard import DashboardService
from app.web.infrastructure.database.repositories import SQLAlchemyDashboardRepository
from app.web.infrastructure.database.connection import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/dashboards", tags=["Dashboards"])

# Get service
async def get_dashboard_service(session: AsyncSession = Depends(get_db_session)):
    repository = SQLAlchemyDashboardRepository(session)
    return DashboardService(repository)

# Routes
@router.get("/", response_model=List[Dashboard])
async def get_dashboards(
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Get all dashboards for the current user"""
    dashboards = await service.get_user_dashboards(current_user["id"])
    return dashboards

@router.post("/", response_model=Dashboard)
async def create_dashboard(
    dashboard: DashboardCreate,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Create a new dashboard"""
    new_dashboard = await service.create_dashboard(current_user["id"], dashboard)
    return new_dashboard

@router.get("/widget-types")
async def get_widget_types(
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Get available widget types"""
    widgets = await service.get_available_widgets()
    return widgets

@router.get("/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Get a specific dashboard by ID"""
    dashboard = await service.get_dashboard(dashboard_id)
    
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
        
    # Check permissions
    if dashboard.user_id != current_user["id"] and not dashboard.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this dashboard")
    
    return dashboard

@router.put("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(
    dashboard_id: str,
    dashboard: DashboardUpdate,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Update an existing dashboard"""
    # Check if dashboard exists and belongs to user
    existing_dashboard = await service.get_dashboard(dashboard_id)
    if not existing_dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
        
    if existing_dashboard.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this dashboard")
    
    updated_dashboard = await service.update_dashboard(dashboard_id, dashboard)
    return updated_dashboard

@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Delete a dashboard"""
    # Check if dashboard exists and belongs to user
    existing_dashboard = await service.get_dashboard(dashboard_id)
    if not existing_dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
        
    if existing_dashboard.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this dashboard")
    
    success = await service.delete_dashboard(dashboard_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete dashboard")
        
    return {"status": "success", "message": f"Dashboard {dashboard_id} deleted"}

@router.post("/{dashboard_id}/widgets", response_model=Widget)
async def add_widget(
    dashboard_id: str,
    widget: WidgetCreate,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Add a widget to a dashboard"""
    # Check if dashboard exists and belongs to user
    existing_dashboard = await service.get_dashboard(dashboard_id)
    if not existing_dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
        
    if existing_dashboard.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this dashboard")
    
    new_widget = await service.add_widget(dashboard_id, widget)
    
    if not new_widget:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add widget")
        
    return new_widget

@router.put("/widgets/{widget_id}", response_model=Widget)
async def update_widget(
    widget_id: str,
    widget_data: dict,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Update a widget"""
    updated_widget = await service.update_widget(widget_id, widget_data)
    
    if not updated_widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
        
    return updated_widget

@router.delete("/widgets/{widget_id}")
async def delete_widget(
    widget_id: str,
    service: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(require_moderator)
):
    """Delete a widget"""
    success = await service.delete_widget(widget_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
        
    return {"status": "success", "message": f"Widget {widget_id} deleted"} 
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.web.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# Models
class DashboardBase(BaseModel):
    title: str
    description: Optional[str] = None
    
class DashboardCreate(DashboardBase):
    widgets: List[dict] = []
    
class Dashboard(DashboardBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    widgets: List[dict] = []
    
    class Config:
        orm_mode = True

# Routes
@router.get("/", response_model=List[Dashboard])
async def get_dashboards(current_user = Depends(get_current_user)):
    """Get all dashboards for the current user"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Implementation depends on your database setup
    # This is a placeholder
    return [
        {
            "id": 1,
            "user_id": current_user["id"],
            "title": "System Overview",
            "description": "System metrics and status",
            "widgets": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 2,
            "user_id": current_user["id"],
            "title": "Game Servers",
            "description": "Game server status and players",
            "widgets": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

@router.post("/", response_model=Dashboard)
async def create_dashboard(dashboard: DashboardCreate, current_user = Depends(get_current_user)):
    """Create a new dashboard"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Implementation depends on your database setup
    # This is a placeholder
    new_dashboard = {
        "id": 1,
        "user_id": current_user["id"],
        "title": dashboard.title,
        "description": dashboard.description,
        "widgets": dashboard.widgets,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return new_dashboard

@router.get("/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(dashboard_id: int, current_user = Depends(get_current_user)):
    """Get a specific dashboard by ID"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Implementation depends on your database setup
    # This is a placeholder
    return {
        "id": dashboard_id, 
        "title": "Sample Dashboard", 
        "description": "Sample description",
        "user_id": current_user["id"],
        "widgets": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.put("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(dashboard_id: int, dashboard: DashboardCreate, current_user = Depends(get_current_user)):
    """Update an existing dashboard"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Implementation depends on your database setup
    # This is a placeholder
    return {
        "id": dashboard_id, 
        "title": dashboard.title, 
        "description": dashboard.description,
        "user_id": current_user["id"],
        "widgets": dashboard.widgets,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: int, current_user = Depends(get_current_user)):
    """Delete a dashboard"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Implementation depends on your database setup
    # This is a placeholder
    return {"status": "success", "message": f"Dashboard {dashboard_id} deleted"} 
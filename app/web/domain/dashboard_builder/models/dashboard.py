from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class WidgetBase(BaseModel):
    """Base model for dashboard widgets"""
    widget_type: str
    title: str
    position_x: int = 0
    position_y: int = 0
    width: int = 2
    height: int = 2
    config: Dict[str, Any] = Field(default_factory=dict)
    
    
class Widget(WidgetBase):
    """Widget model with ID"""
    id: str
    dashboard_id: str
    created_at: datetime
    updated_at: datetime


class WidgetCreate(WidgetBase):
    """Model for creating a new widget"""
    pass


class DashboardBase(BaseModel):
    """Base model for dashboards"""
    title: str
    description: Optional[str] = None
    layout_config: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool = False
    

class Dashboard(DashboardBase):
    """Dashboard model with ID and metadata"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    widgets: List[Widget] = Field(default_factory=list)
    
    class Config:
        orm_mode = True


class DashboardCreate(DashboardBase):
    """Model for creating a new dashboard"""
    widgets: List[WidgetCreate] = Field(default_factory=list)


class DashboardUpdate(DashboardBase):
    """Model for updating an existing dashboard"""
    widgets: List[Dict[str, Any]] = Field(default_factory=list) 
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schema for dashboard configuration properties
class DashboardConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User-defined name for the dashboard configuration.")
    dashboard_type: str = Field(..., description="The functional type of the dashboard (e.g., 'welcome', 'monitoring').")
    description: Optional[str] = Field(None, max_length=500, description="Optional description for the dashboard configuration.")
    config: Optional[Dict[str, Any]] = Field(None, description="JSON configuration defining the dashboard structure and components.")

# Schema for the payload when creating a new dashboard configuration
class DashboardConfigCreatePayload(DashboardConfigBase):
    pass # Inherits all fields from Base

# Schema for the payload when updating an existing dashboard configuration
class DashboardConfigUpdatePayload(DashboardConfigBase):
    # Making all fields optional for partial updates
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    dashboard_type: Optional[str] = None 
    description: Optional[str] = Field(None, max_length=500) # Added description
    config: Optional[Dict[str, Any]] = None 

# Schema for the response when returning dashboard configuration details
class DashboardConfigResponseSchema(DashboardConfigBase):
    id: int = Field(..., description="Unique database ID of the dashboard configuration.")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Allow creating schema from ORM objects 
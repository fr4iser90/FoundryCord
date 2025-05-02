from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schema for dashboard instance properties
class DashboardInstanceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User-defined name for the dashboard instance.")
    dashboard_type: str = Field(..., description="The functional type of the dashboard (e.g., 'welcome', 'monitoring').")
    config: Optional[Dict[str, Any]] = Field(None, description="JSON configuration specific to this dashboard instance.")

# Schema for the payload when creating a new dashboard instance linked to a channel template
class DashboardInstanceCreatePayload(DashboardInstanceBase):
    pass # Inherits all fields from Base

# Schema for the payload when updating an existing dashboard instance
class DashboardInstanceUpdatePayload(DashboardInstanceBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    dashboard_type: Optional[str] = None # Usually type shouldn't change, but allow if needed
    config: Optional[Dict[str, Any]] = None
    # Making all fields optional for partial updates

# Schema for the response when returning dashboard instance details
class DashboardInstanceResponseSchema(DashboardInstanceBase):
    id: int = Field(..., description="Unique database ID of the dashboard instance.")
    guild_template_channel_id: int = Field(..., description="ID of the guild template channel this instance is linked to.")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Allow creating schema from ORM objects 
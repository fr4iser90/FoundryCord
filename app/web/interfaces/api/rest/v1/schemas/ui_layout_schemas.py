from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime # Import datetime

# --- Schemas for Listing Layout Templates --- #

class LayoutTemplateInfoSchema(BaseModel):
    """Basic information about a saved layout template."""
    layout_id: str = Field(..., description="The unique identifier for the saved layout (e.g., page_identifier).")
    name: str = Field(..., description="A user-friendly name for the template (if implemented).")
    # Add flags as needed - assuming they exist in the data source
    is_shared: Optional[bool] = Field(False, description="Whether this template is shared.") 
    is_initial: Optional[bool] = Field(False, description="Whether this is the initial snapshot.") 
    updated_at: Optional[datetime] = Field(None, description="When the layout was last saved.")

    class Config:
        from_attributes = True # Enable ORM mode if data comes from DB models

class LayoutTemplateListResponse(BaseModel):
    """Response containing a list of available layout templates."""
    templates: List[LayoutTemplateInfoSchema]

# --- Schemas for Saving/Loading a Single Layout --- #

class GridstackItem(BaseModel):
    x: int
    y: int
    w: int
    h: int # Ensure h is required as per frontend validation error
    id: str | int
    # Keep allowing extra fields Gridstack might send
    class Config:
        extra = 'allow'

class UILayoutSaveSchema(BaseModel):
    """Payload sent from frontend when saving a layout."""
    layout: List[GridstackItem] = Field(..., description="The Gridstack layout data.")
    is_locked: bool = Field(..., description="The current lock state of the layout.")
    # Optional: Add name if we allow naming layouts on save?
    # name: Optional[str] = None 

class UILayoutResponseSchema(BaseModel):
    """Response schema when retrieving a single layout's details."""
    page_identifier: str
    layout: List[GridstackItem]
    is_locked: bool # Return lock state when loading
    name: Optional[str] = None # Return name if available
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

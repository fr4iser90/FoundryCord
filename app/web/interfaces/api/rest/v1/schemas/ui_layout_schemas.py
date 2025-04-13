from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime # Import datetime

# --- Schemas for Listing Layout Templates --- #

class LayoutTemplateInfoSchema(BaseModel):
    """Schema for providing basic information about a layout template (initial or saved)."""
    layout_id: str = Field(..., description="Identifier used to load this template (e.g., page_identifier or shared template name).")
    name: str = Field(..., description="Display name of the template.")
    is_shared: Optional[bool] = Field(False, description="Indicates if this is a shared template.")
    is_initial: Optional[bool] = Field(False, description="Indicates if this is the initial snapshot template.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update.")

    class Config:
        from_attributes = True # Enable ORM mode if data comes from DB models

class LayoutTemplateListResponse(BaseModel):
    """Response schema for listing available layout templates."""
    templates: List[LayoutTemplateInfoSchema]

# --- Schemas for Saving/Loading a Single Layout --- #

class GridstackItem(BaseModel):
    """Represents a single widget item in the Gridstack layout."""
    id: str = Field(..., description="Unique identifier for the widget.")
    x: int = Field(..., description="X coordinate (column) of the widget.")
    y: int = Field(..., description="Y coordinate (row) of the widget.")
    w: int = Field(..., description="Width of the widget in columns.")
    h: int = Field(..., description="Height of the widget in rows.")
    content: Optional[str] = Field(None, description="Optional HTML content or identifier.")
    # Add other potential gridstack properties if needed (e.g., noResize, noMove)

class UILayoutSaveSchema(BaseModel):
    """Schema for saving the layout state, including items and lock status."""
    layout: List[GridstackItem] = Field(..., description="List of widget items in the layout.")
    is_locked: bool = Field(False, description="Indicates if the layout is locked for editing.")
    # Optional: Add name if layouts can be named directly on save
    # name: Optional[str] = Field(None, description="Optional name for the saved layout.")

class UILayoutResponseSchema(BaseModel):
    """Schema for responding with the full layout state."""
    page_identifier: str = Field(..., description="The unique identifier for the page this layout belongs to.")
    layout: List[GridstackItem] = Field(..., description="List of widget items.")
    is_locked: bool = Field(..., description="Current lock status of the layout.")
    name: Optional[str] = Field(None, description="Optional name associated with the layout.") # From layout_data or entity
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update.")

# --- New Schema for Sharing --- 
class LayoutShareRequestSchema(BaseModel):
    """Schema for the request body when sharing a layout as a template."""
    template_name: str = Field(..., min_length=3, max_length=100, description="The unique name for the shared template.")
    template_description: Optional[str] = Field(None, max_length=500, description="Optional description for the shared template.")

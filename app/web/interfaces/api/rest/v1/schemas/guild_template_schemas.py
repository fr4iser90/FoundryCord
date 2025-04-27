from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GuildTemplateCreateSchema(BaseModel):
    """Schema for creating a new guild template from an existing guild."""
    template_name: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description="Unique name for the new template.",
        examples=["My Standard Server Template"]
    )
    template_description: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Optional description for the template.",
        examples=["A basic template with general channels and roles."]
    )

    # Note: source_guild_id is taken from the URL path parameter in the controller,
    # so it doesn't need to be in the request body schema.

# --- Schema for Sharing/Copying a Template ---
class GuildTemplateShareSchema(BaseModel):
    """Schema for the request body when sharing/copying a template."""
    original_template_id: int = Field(..., description="The database ID of the template to be copied.")
    new_template_name: str = Field(..., min_length=3, max_length=100, description="The unique name for the new shared template.")
    new_template_description: Optional[str] = Field(None, max_length=500, description="Optional description for the new shared template.")

# --- Schemas for Template Response ---

class PermissionSchema(BaseModel):
    """Schema for category or channel permissions within a template."""
    id: int
    role_name: str
    allow: int = Field(..., alias="allow_permissions_bitfield", serialization_alias="allow")
    deny: int = Field(..., alias="deny_permissions_bitfield", serialization_alias="deny")

    class Config:
        populate_by_name = True # Allow using alias names for population

class CategorySchema(BaseModel):
    """Schema for a category within a template."""
    id: int
    name: str = Field(..., alias="category_name")
    position: int
    permissions: List[PermissionSchema] = []

    class Config:
        populate_by_name = True # Allow using alias names for population

class ChannelSchema(BaseModel):
    """Schema for a channel within a template."""
    id: int
    name: str = Field(..., alias="channel_name")
    type: str
    position: int
    topic: Optional[str] = None
    is_nsfw: Optional[bool] = False
    slowmode_delay: Optional[int] = 0
    parent_category_template_id: Optional[int] = None # Link to category within the template
    permissions: List[PermissionSchema] = []

    class Config:
        populate_by_name = True # Allow using alias names for population

class GuildTemplateResponseSchema(BaseModel):
    """Schema for the detailed response when fetching a guild template."""
    guild_id: Optional[str] = None # Original guild ID, may be null if template is generic
    template_id: int
    template_name: str
    created_at: Optional[datetime] = None
    categories: List[CategorySchema] = []
    channels: List[ChannelSchema] = []

    class Config:
        # from_attributes = True # REMOVED - Data comes from a dict, not ORM object directly here
        populate_by_name = True # Enable using aliases for population
        # Ensure nested models also use populate_by_name if needed

# Optional: Add other schemas later if needed, e.g., for responses
# class GuildTemplateResponseSchema(BaseModel):
#     id: int
#     name: str
#     description: Optional[str]
#     # ... other fields ...
#
#     class Config:
#         orm_mode = True # If mapping from ORM objects

# --- Schema for Template List Response ---

class GuildTemplateListItemSchema(BaseModel):
    """Schema for a single item in the template list response."""
    template_id: int
    template_name: str
    created_at: Optional[datetime] = None
    guild_id: Optional[str] = None # Include the source guild ID if available
    creator_user_id: Optional[int] = None # Add creator user ID (optional)

    class Config:
        from_attributes = True # Needed if data comes directly from ORM objects/dicts

class GuildTemplateListResponseSchema(BaseModel):
    """Schema for the response when listing guild templates."""
    templates: List[GuildTemplateListItemSchema]

# --- NEW Schemas for Structure Update --- 

class GuildStructureNodeUpdate(BaseModel):
    id: str = Field(..., description="Node ID from jsTree (e.g., 'category_123', 'channel_456')")
    parent_id: Optional[str] = Field(None, description="Parent Node ID from jsTree (e.g., 'category_123', 'template_root') or None for root-level items")
    position: int = Field(..., ge=0, description="New 0-based index position among siblings")
    # Add other fields if frontend supports editing them via tree/properties, e.g.:
    # name: Optional[str] = None 
    # topic: Optional[str] = None

class GuildStructureUpdatePayload(BaseModel):
    nodes: List[GuildStructureNodeUpdate] = Field(..., description="List of all nodes representing the desired structure")

# Schema for the response (if any)
class GuildStructureUpdateResponse(BaseModel):
    message: str
    updated_template_id: int

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Schemas for Permissions (Used by Channel/Category) ---
class GuildTemplatePermissionBase(BaseModel):
    role_id: Optional[int] = None
    permission_type: str # e.g., 'allow', 'deny'
    permission_key: str # e.g., 'view_channel', 'send_messages'

class GuildTemplatePermissionCreate(GuildTemplatePermissionBase):
    pass

class GuildTemplatePermission(GuildTemplatePermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Schemas for Channels (Used by Category/Template Detail) ---
class GuildChannelTemplateBase(BaseModel):
    channel_name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50) # 'text', 'voice', etc.
    topic: Optional[str] = Field(None, max_length=1024)
    position: int = Field(..., ge=0)
    parent_category_template_id: Optional[int] = None

class GuildChannelTemplateCreate(GuildChannelTemplateBase):
    permissions: List[GuildTemplatePermissionCreate] = []

class GuildChannelTemplate(GuildChannelTemplateBase):
    id: int
    structure_template_id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[GuildTemplatePermission] = []

    class Config:
        from_attributes = True

# --- Schemas for Categories (Used by Template Detail) ---
class GuildCategoryTemplateBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100)
    position: int = Field(..., ge=0)

class GuildCategoryTemplateCreate(GuildCategoryTemplateBase):
    permissions: List[GuildTemplatePermissionCreate] = []
    channels: List[GuildChannelTemplateCreate] = []

class GuildCategoryTemplate(GuildCategoryTemplateBase):
    id: int
    structure_template_id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[GuildTemplatePermission] = []
    channels: List[GuildChannelTemplate] = []

    class Config:
        from_attributes = True

# --- Base Schemas for Structure Templates --- 
class GuildStructureTemplateBase(BaseModel):
    template_name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_shared: bool = False

class GuildStructureTemplateCreate(GuildStructureTemplateBase):
    # On creation, structure is often defined separately or copied
    # Now GuildCategoryTemplateCreate is defined
    categories: List[GuildCategoryTemplateCreate] = []

class GuildStructureTemplate(GuildStructureTemplateBase):
    id: int
    creator_user_id: int
    created_at: datetime
    updated_at: datetime
    is_initial_snapshot: bool = False
    template_delete_unmanaged: Optional[bool] = None # Get from GuildConfig
    # The full structure might be loaded separately for performance
    class Config:
        from_attributes = True

# --- Informational/Detail Schemas for Templates --- 
class GuildStructureTemplateInfo(BaseModel):
    template_id: int
    template_name: str
    description: Optional[str]
    is_shared: bool
    is_initial_snapshot: bool
    creator_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class GuildStructureTemplateDetail(GuildStructureTemplate):
    # Now GuildCategoryTemplate and GuildChannelTemplate are defined
    categories: List[GuildCategoryTemplate] = []
    channels: List[GuildChannelTemplate] = [] 

# --- Schemas for Structure Update --- 
class GuildStructureNodeUpdate(BaseModel):
    id: str = Field(..., description="Node ID from jsTree (e.g., 'category_123', 'channel_456')")
    parent_id: Optional[str] = Field(None, description="Parent Node ID from jsTree (e.g., 'category_123', 'template_root') or None for root-level items")
    position: int = Field(..., ge=0, description="New 0-based index position among siblings")
    name: Optional[str] = Field(None, description="Display name extracted from the node")
    channel_type: Optional[str] = Field(None, description="Type of channel (e.g., 'text', 'voice'), only for channel nodes")

class GuildStructureUpdatePayload(BaseModel):
    nodes: List[GuildStructureNodeUpdate] = Field(..., description="List of all nodes representing the desired structure")
    property_changes: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Dictionary mapping node keys (e.g., 'category_123') to changed properties and their new values.")

class GuildStructureUpdateResponse(BaseModel):
    message: str
    updated_template_id: int

# --- Schema for Creating Template from Structure --- 
class GuildStructureTemplateCreateFromStructure(BaseModel):
    new_template_name: str = Field(..., min_length=3, max_length=100, description="The name for the new template.")
    new_template_description: Optional[str] = Field(None, max_length=500, description="Optional description for the new template.")
    # Now GuildStructureUpdatePayload is defined
    structure: GuildStructureUpdatePayload = Field(..., description="The structure payload containing the list of nodes (categories/channels) with their parents and positions.")


# --- LEGACY SCHEMAS (Likely replaceable by the ones above) ---
# Keep existing schemas at the end for now to avoid breaking other parts, 
# but they should be reviewed and potentially removed/merged later.

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

class GuildTemplateShareSchema(BaseModel):
    """Schema for the request body when sharing/copying a template."""
    original_template_id: int = Field(..., description="The database ID of the template to be copied.")
    new_template_name: str = Field(..., min_length=3, max_length=100, description="The unique name for the new shared template.")
    new_template_description: Optional[str] = Field(None, max_length=500, description="Optional description for the new shared template.")

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
    is_initial_snapshot: Optional[bool] = False # Indicates if it's the initial auto-generated snapshot
    template_delete_unmanaged: Optional[bool] = None # Get from GuildConfig

    class Config:
        from_attributes = True
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

# --- NEW: Schema for updating template metadata (e.g., name) ---
class GuildTemplateMetadataUpdateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="The new name for the template.")
    # Add description later if needed

# Schema for Node representation in structure updates/creation
class NodeSchema(BaseModel):
    id: str # Frontend ID (e.g., "category_123" or "channel_456")
    parent_id: str # Frontend ID of the parent
    position: int
    name: str = Field(..., min_length=1, max_length=100)
    channel_type: Optional[str] = None # Only for channels (e.g., 'text', 'voice')

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v

    @validator('channel_type')
    def channel_type_valid(cls, v, values):
        if 'id' in values and values['id'].startswith('channel_') and v not in ['text', 'voice']: # Add other valid types
            raise ValueError(f"Invalid channel type: {v}")
        return v

# --- NEW: Schema for Pending Property Changes ---
class PropertyChangeValue(BaseModel):
    # Define fields based on what properties can change, e.g.:
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    topic: Optional[str] = Field(None, max_length=1024) # Example length
    is_nsfw: Optional[bool] = None
    slowmode_delay: Optional[int] = Field(None, ge=0, le=21600) # Discord limits (0-6h)
    # Add other properties like permissions later

# Schema for the payload of the structure update endpoint
class GuildStructureUpdatePayload(BaseModel):
    nodes: List[NodeSchema] = Field(..., description="The complete list of nodes representing the desired structure.")
    # --- NEW: Add property_changes field --- 
    property_changes: Optional[Dict[str, PropertyChangeValue]] = Field(None, description="Dictionary of pending property changes keyed by node ID.")
    # The keys in property_changes should match the 'id' field in NodeSchema (e.g., "category_123")

# Simplified node for response
class SimpleNodeSchema(BaseModel):
    id: int # Database ID
    name: str
    # Add other relevant fields like type if needed

class GuildStructureUpdateResponse(BaseModel):
    message: str
    updated_nodes: List[SimpleNodeSchema] # Or more detailed info if needed


# Schema for CREATING a template FROM a structure payload
class GuildStructureTemplateCreateFromStructure(BaseModel):
    new_template_name: str = Field(..., min_length=3, max_length=100)
    new_template_description: Optional[str] = Field(None, max_length=255)
    structure: GuildStructureUpdatePayload # Reuse the structure update payload

# Schema for returning basic info about a newly created template
class GuildStructureTemplateInfo(BaseModel):
    template_id: int
    template_name: str
    message: str

# Schema for sharing a template (creating a shared copy)
class GuildTemplateShareSchema(BaseModel):
    original_template_id: int = Field(..., description="The ID of the template to copy and share.")
    new_template_name: str = Field(..., min_length=3, max_length=100, description="The name for the new shared template copy.")
    new_template_description: Optional[str] = Field(None, max_length=255, description="Optional description for the shared copy.")


# --- Response Schemas --- 

class CategoryResponseSchema(BaseModel):
    id: int
    template_id: int
    category_name: str
    position: int
    # Permissions might be added later

    class Config:
        orm_mode = True
        allow_population_by_field_name = True # Allows using db column names

class ChannelResponseSchema(BaseModel):
    id: int
    template_id: int
    parent_category_template_id: Optional[int] # Changed from category_id
    channel_name: str
    type: str # e.g., 'text', 'voice'
    position: int
    topic: Optional[str] = None # Make optional
    is_nsfw: Optional[bool] = None # Make optional
    slowmode_delay: Optional[int] = None # Make optional
    # Permissions might be added later

    class Config:
        orm_mode = True
        allow_population_by_field_name = True # Allows using db column names

class GuildTemplateResponseSchema(BaseModel):
    template_id: int
    creator_user_id: int
    template_name: str
    description: Optional[str]
    created_at: str # Keep as string for simplicity
    updated_at: str
    is_shared: bool
    is_initial_snapshot: bool = False # Add this flag
    template_delete_unmanaged: bool = False # Added setting
    categories: List[CategoryResponseSchema]
    channels: List[ChannelResponseSchema]

    class Config:
        orm_mode = True # Useful if data comes directly from ORM model
        allow_population_by_field_name = True

# For listing multiple templates (simplified view)
class BasicGuildTemplateInfo(BaseModel):
    template_id: int
    creator_user_id: Optional[int] = None # Can be None for initial snapshot
    template_name: str
    created_at: str
    is_shared: bool
    is_initial_snapshot: bool = False # Add flag here too

class GuildTemplateListResponseSchema(BaseModel):
    templates: List[BasicGuildTemplateInfo]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Ensure all models are loaded 
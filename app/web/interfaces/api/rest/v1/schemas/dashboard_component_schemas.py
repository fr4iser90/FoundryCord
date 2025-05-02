"""
Pydantic schemas for Dashboard Component Definitions API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

# --- Supporting Schemas --- 

class ComponentConfigFieldOptionSchema(BaseModel):
    """Schema for an option within a 'select' field."""
    value: str
    label: str

class ComponentValidationRuleSchema(BaseModel):
    """Schema for a single validation rule."""
    rule_type: Literal['required', 'maxLength', 'minLength', 'pattern']
    value: Any # e.g., True for required, 100 for maxLength, regex string for pattern
    message: Optional[str] = None # Optional custom error message

class ComponentConfigFieldSchema(BaseModel):
    """Schema defining a single configurable field within a component definition."""
    key: str = Field(..., description="Technical key for this config field (e.g., 'button_label')")
    label: str = Field(..., description="Display name for the editor UI (e.g., 'Button Text')")
    field_type: Literal[
        'text', 'textarea', 'number', 'color', 'select', 
        'checkbox', 'image_upload', 'user_select', 'channel_select' # Add more as needed
    ] = Field(..., description="Type of the input field in the editor")
    default_value: Optional[Any] = Field(None, description="Default value for this field")
    options: Optional[List[ComponentConfigFieldOptionSchema]] = Field(None, description="Options for 'select' field type")
    validation: Optional[List[ComponentValidationRuleSchema]] = Field(None, description="Validation rules for the field")
    help_text: Optional[str] = Field(None, description="Explanatory text shown to the user in the editor")
    supports_variables: Optional[bool] = Field(False, description="Whether this field supports template variables like {{user_name}}")

class ComponentMetadataSchema(BaseModel):
    """Schema for the metadata of a component definition."""
    display_name: str = Field(..., description="User-friendly name of the component")
    description: Optional[str] = Field(None, description="Brief description of the component")
    icon: Optional[str] = Field(None, description="Icon class (e.g., Font Awesome) for the toolbox/editor")
    category: Optional[str] = Field('Other', description="Category for grouping components in the toolbox")

class PreviewHintsSchema(BaseModel):
    """Schema for optional hints for the preview renderer."""
    layout: Optional[Literal['inline', 'block']] = 'block'
    discord_equivalent: Optional[str] = None # E.g., "Embed Field", "Button Row"
    # Add more hints as needed

# --- Main Schema --- 

class ComponentDefinitionSchema(BaseModel):
    """Schema representing a complete dashboard component definition."""
    id: int # Database ID
    component_key: str = Field(..., description="Unique key identifying this definition (e.g., 'common_embed_footer')")
    dashboard_type: str = Field(..., description="Scope/Type of dashboard this applies to (e.g., 'common', 'welcome')")
    component_type: str = Field(..., description="Type of the component itself (e.g., 'embed', 'button')")
    metadata: ComponentMetadataSchema = Field(..., description="Display metadata")
    config_schema: List[ComponentConfigFieldSchema] = Field(..., description="Schema describing the configurable fields")
    preview_hints: Optional[PreviewHintsSchema] = Field(None, description="Hints for rendering the preview")

    class Config:
        orm_mode = True # Enable reading data directly from ORM models

# --- Response Schema --- 

class ComponentDefinitionListResponseSchema(BaseModel):
    """Schema for the API response containing a list of component definitions."""
    components: List[ComponentDefinitionSchema] 
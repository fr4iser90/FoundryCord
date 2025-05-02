from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GuildInfo(BaseModel):
    """Schema for representing basic guild information in API responses."""
    id: str = Field(..., alias='guild_id', description="The Discord Guild ID.")
    name: str
    icon_url: Optional[str] = Field(None, description="URL of the guild icon, can be None.")
    member_count: int = Field(default=0)
    access_status: str
    # Add relevant date fields if needed for display consistency
    access_requested_at: Optional[datetime] = None
    access_reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None # Assuming GuildEntity has this
    
    # Add other relevant fields from GuildEntity if needed, e.g.:
    # owner_id: Optional[str] 
    # enable_commands: bool

    class Config:
        from_attributes = True  # Replaces orm_mode
        populate_by_name = True # Replaces allow_population_by_field_name

# New schema for the access update response
class GuildAccessUpdateResponse(BaseModel):
    """Schema for the response after updating guild access status."""
    message: str
    guild: GuildInfo # Embed the GuildInfo schema



# You might want to add other guild-related schemas here in the future,
# e.g., GuildDetails, GuildSettings, etc.

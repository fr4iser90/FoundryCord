from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Define the structure we expect from Gridstack's save() method.
# This might need adjustment based on the exact output of grid.save().
# It typically includes grid items with x, y, w, h, id.
class GridstackItem(BaseModel):
    x: int
    y: int
    w: int
    h: int
    id: str | int # Sometimes id can be string or int
    # Add other potential fields like content, noResize, noMove etc. if needed
    # Be flexible with Any for potential custom data
    # content: str | None = None
    # noResize: bool | None = None
    # noMove: bool | None = None 
    # ... any other fields Gridstack might add

    class Config:
        extra = 'allow' # Allow extra fields not explicitly defined

# The main layout payload for saving
class UILayoutSaveSchema(BaseModel):
    layout: List[GridstackItem] = Field(..., description="The Gridstack layout data as an array of items.")

# The response schema when retrieving a layout
class UILayoutResponseSchema(BaseModel):
    page_identifier: str
    layout: List[GridstackItem] # Return the same structure as saved

    class Config:
        orm_mode = True # Enable compatibility with ORM models if needed later, although we return dict

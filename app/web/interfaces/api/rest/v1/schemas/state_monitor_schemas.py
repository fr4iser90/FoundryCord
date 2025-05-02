"""
Pydantic Schemas for State Monitor API Payloads.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
import time

# --- Schemas for data coming FROM the browser to /log-browser-snapshot ---

class BrowserCollectorDataBase(BaseModel):
    """Base for specific browser collector data."""
    # Add common fields if any, otherwise just acts as a marker
    pass

class NavigationData(BrowserCollectorDataBase):
    url: Optional[str] = None
    path: Optional[str] = None
    query: Optional[Dict[str, str]] = None
    hash: Optional[str] = None

class ViewportData(BrowserCollectorDataBase):
    width: Optional[int] = None
    height: Optional[int] = None
    devicePixelRatio: Optional[float] = None
    orientation: Optional[str] = None # e.g., 'portrait', 'landscape'

class JsErrorData(BaseModel):
    """Structure for a single JavaScript error."""
    message: Optional[str] = None
    source: Optional[str] = None
    lineno: Optional[int] = None
    colno: Optional[int] = None
    stack: Optional[str] = None
    timestamp: Optional[float] = None # JS timestamp (ms)

class ConsoleLogData(BaseModel):
    """Structure for a single console log entry."""
    level: str # e.g., 'log', 'warn', 'error'
    message: str
    timestamp: Optional[float] = None # JS timestamp (ms)
    # args: Optional[List[Any]] = None # Avoid Any if possible, maybe stringified?

class BrowserSnapshotResults(BaseModel):
    """Defines the expected 'results' object from browser snapshots."""
    navigation: Optional[NavigationData] = None
    viewport: Optional[ViewportData] = None
    # features: Optional[Dict[str, bool]] = None # Add if sent
    # domSummary: Optional[Dict[str, Any]] = None # Add if sent
    # storageKeys: Optional[Dict[str, List[str]]] = None # Add if sent
    javascriptErrors: Optional[List[JsErrorData]] = Field(default_factory=list)
    consoleLogs: Optional[List[ConsoleLogData]] = Field(default_factory=list)
    # computedStyles: Optional[Dict[str, str]] = None # Add if sent

    class Config:
        extra = 'ignore' # Ignore extra fields sent by browser collectors

class ErrorContextForPayload(BaseModel):
    """Context specific to the error that triggered the snapshot."""
    message: Optional[str] = None
    source: Optional[str] = None
    lineno: Optional[int] = None
    colno: Optional[int] = None
    # stack: Optional[str] = None # Maybe redundant if in javascriptErrors?

class SnapshotContextForPayload(BaseModel):
    """Defines the 'context' object expected in the payload."""
    trigger: str = Field(..., pattern="^js_error$") # Force trigger to be 'js_error'
    error: Optional[ErrorContextForPayload] = None

class SnapshotLogPayload(BaseModel):
    """
    Defines the overall structure of the JSON body expected by the
    POST /log-browser-snapshot endpoint.
    """
    # timestamp: float # JS timestamp (ms), validate range?
    results: BrowserSnapshotResults
    context: SnapshotContextForPayload

    @validator('results')
    def check_at_least_one_result(cls, v):
        # Ensure at least some data is present, even if just errors/logs
        if not v.navigation and not v.viewport and not v.javascriptErrors and not v.consoleLogs:
             # Allow empty results if needed, otherwise raise error
             # raise ValueError('Snapshot results cannot be completely empty')
             pass # Allow empty for now
        return v

# --- Schemas for data going TO the browser (e.g., from GET endpoints) ---

class StateSnapshotMetadata(BaseModel):
    """Metadata for listing snapshots."""
    snapshot_id: str
    capture_timestamp: float # Unix timestamp (seconds)
    trigger: str
    context: Optional[Dict[str, Any]] = None

    class Config:
        # orm_mode = True # If loading from SQLAlchemy model
        from_attributes = True

class FullSnapshotData(BaseModel):
    """Represents the full snapshot data structure (server + browser)."""
    server: Optional[Dict[str, Any]] = None
    browser: Optional[BrowserSnapshotResults] = None # Reuse browser schema

class StoredSnapshotResponse(BaseModel):
    """Response model for retrieving a single stored snapshot."""
    snapshot_id: str
    capture_timestamp: float # Unix timestamp (seconds)
    trigger: str
    context: Optional[Dict[str, Any]] = None
    snapshot: FullSnapshotData

    class Config:
        # orm_mode = True
        from_attributes = True 
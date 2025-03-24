from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class DashboardComponentModel:
    """Domain model for dashboard components"""
    id: Optional[int] = None
    component_type: str = ""
    component_name: str = ""
    custom_id: Optional[str] = None
    position: int = 0
    is_active: bool = True
    config: Dict[str, Any] = None
    data_source_id: Optional[str] = None

@dataclass
class DashboardModel:
    """Domain model for dashboards"""
    # Required parameters first (no defaults)
    dashboard_type: str
    name: str
    # Optional parameters next (with defaults)
    id: Optional[int] = None
    description: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    is_active: bool = True
    update_frequency: int = 300  # In seconds
    config: Dict[str, Any] = None
    components: List[DashboardComponentModel] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.config is None:
            self.config = {}
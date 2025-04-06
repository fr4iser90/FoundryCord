from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.shared.infrastructure.models.discord.enums.dashboard import DashboardType, ComponentType

@dataclass
class DashboardComponentModelEntity:
    """Domain model for dashboard components"""
    id: Optional[int] = None
    component_type: ComponentType = ComponentType.CUSTOM
    component_name: str = ""
    custom_id: Optional[str] = None
    position: int = 0
    is_active: bool = True
    config: Dict[str, Any] = None
    data_source_id: Optional[str] = None

@dataclass
class DashboardModelEntity:
    """Domain model for dashboards"""
    # Required parameters first (no defaults)
    dashboard_type: DashboardType
    name: str
    # Optional parameters next (with defaults)
    id: Optional[int] = None
    description: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    is_active: bool = True
    update_frequency: int = 300  # In seconds
    config: Dict[str, Any] = None
    components: List[DashboardComponentModelEntity] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.config is None:
            self.config = {}
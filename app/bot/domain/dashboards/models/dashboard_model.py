"""Core domain models for the dashboard system."""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

class ComponentType(Enum):
    """Types of components available in dashboards."""
    STATUS_INDICATOR = "status_indicator"
    METRIC_DISPLAY = "metric_display"
    CHART = "chart"
    BUTTON_GROUP = "button_group"
    TEXT_SECTION = "text_section"
    EMBED_FIELD = "embed_field"
    SERVER_LIST = "server_list"
    USER_LIST = "user_list"
    REFRESH_BUTTON = "refresh_button"
    NAVIGATION_BUTTON = "navigation_button"

@dataclass
class ComponentConfig:
    """Component configuration within a dashboard"""
    id: str
    type: str
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LayoutItem:
    """Layout item for dashboard UI."""
    component_id: str
    position_x: int = 0
    position_y: int = 0
    width: int = 1
    height: int = 1

@dataclass
class DataSourceConfig:
    """Configuration for a dashboard data source."""
    id: str
    source_type: str
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardModel:
    """Domain model for dashboard configurations"""
    id: str
    name: str
    channel_id: int
    guild_id: int
    type: str = "default"  # Add default type
    description: Optional[str] = None
    components: List[ComponentConfig] = field(default_factory=list)
    message_id: Optional[int] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_new(cls, name: str, channel_id: int, guild_id: int, 
                  dashboard_type: str = "default", description: Optional[str] = None):
        """Factory method to create a new dashboard"""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            channel_id=channel_id,
            guild_id=guild_id,
            type=dashboard_type,
            description=description
        )
    
    def add_component(self, component: ComponentConfig):
        """Add a component to the dashboard."""
        self.components.append(component)
        
    def add_data_source(self, data_source: DataSourceConfig):
        """Add a data source to the dashboard."""
        self.data_sources[data_source.id] = data_source
        
    def add_layout_item(self, layout_item: LayoutItem):
        """Add a layout item to the dashboard."""
        self.layout.append(layout_item) 
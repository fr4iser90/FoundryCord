"""Core domain models for the dashboard system."""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

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
    """Configuration for a dashboard component."""
    id: str
    component_type: str
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
    """Core domain model for a dashboard."""
    id: str
    type: str
    title: str
    description: Optional[str] = None
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    category_name: Optional[str] = None
    channel_name: Optional[str] = None
    message_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    components: List[ComponentConfig] = field(default_factory=list)
    data_sources: Dict[str, DataSourceConfig] = field(default_factory=dict)
    layout: List[LayoutItem] = field(default_factory=list)
    embed: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, Any] = field(default_factory=dict)
    interactive_components: List[str] = field(default_factory=list)
    
    def add_component(self, component: ComponentConfig):
        """Add a component to the dashboard."""
        self.components.append(component)
        
    def add_data_source(self, data_source: DataSourceConfig):
        """Add a data source to the dashboard."""
        self.data_sources[data_source.id] = data_source
        
    def add_layout_item(self, layout_item: LayoutItem):
        """Add a layout item to the dashboard."""
        self.layout.append(layout_item) 
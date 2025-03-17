"""Component domain models for the dashboard system."""
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

class ComponentStyle(Enum):
    """Visual styles for components."""
    DEFAULT = "default"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ComponentModel:
    """Base domain model for a dashboard component."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = "component"
    title: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 1
    height: int = 1
    config: Dict[str, Any] = field(default_factory=dict)
    visible: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "width": self.width,
            "height": self.height,
            "config": self.config,
            "visible": self.visible
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentModel':
        """Create component from dictionary representation."""
        return cls(
            id=data.get("id", str(uuid4())),
            type=data.get("type", "component"),
            title=data.get("title"),
            position_x=data.get("position_x", 0),
            position_y=data.get("position_y", 0),
            width=data.get("width", 1),
            height=data.get("height", 1),
            config=data.get("config", {}),
            visible=data.get("visible", True)
        )

@dataclass
class ButtonModel:
    """Domain model for a button component."""
    label: str
    action: str
    style: ComponentStyle = ComponentStyle.PRIMARY
    emoji: Optional[str] = None
    disabled: bool = False
    custom_id: Optional[str] = None
    url: Optional[str] = None
    
@dataclass
class MetricModel:
    """Domain model for a metric display component."""
    title: str
    value: Any
    format: str = "{value}"
    icon: Optional[str] = None
    thresholds: Dict[str, float] = field(default_factory=dict)
    
@dataclass
class ChartDataPoint:
    """Data point for a chart component."""
    label: str
    value: float
    
@dataclass
class ChartModel:
    """Domain model for a chart component."""
    title: str
    data_points: List[ChartDataPoint]
    chart_type: str = "bar"  # bar, line, pie
    color_scheme: List[str] = field(default_factory=list)
    
@dataclass
class ServerStatusModel:
    """Domain model for a server status component."""
    name: str
    status: str
    address: Optional[str] = None
    port: Optional[int] = None
    player_count: Optional[int] = None
    max_players: Optional[int] = None
    version: Optional[str] = None
    
@dataclass
class TextSectionModel:
    """Domain model for a text section component."""
    title: Optional[str] = None
    content: str = ""
    inline: bool = False 
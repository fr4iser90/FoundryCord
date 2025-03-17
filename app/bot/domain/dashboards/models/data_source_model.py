"""Data source domain models for the dashboard system."""
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class DataSourceType(Enum):
    """Types of data sources available."""
    SYSTEM_METRICS = "system_metrics"
    DOCKER_METRICS = "docker_metrics"
    MINECRAFT_SERVER = "minecraft_server"
    WEB_SERVICE = "web_service"
    DATABASE = "database"
    PROJECT = "project"
    USER_METRICS = "user_metrics"
    STATIC = "static"

@dataclass
class DataSourceParams:
    """Parameters for a data source."""
    refresh_interval: int = 60
    timeout: int = 10
    cache_ttl: int = 300
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataSourceResult:
    """Result from a data source query."""
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
    source_id: Optional[str] = None
    cached: bool = False
    
@dataclass
class DataSourceModel:
    """Domain model for a data source."""
    id: str
    type: DataSourceType
    name: str
    description: Optional[str] = None
    params: DataSourceParams = field(default_factory=DataSourceParams)
    last_result: Optional[DataSourceResult] = None
    last_update: Optional[datetime] = None
    
    async def fetch_data(self) -> DataSourceResult:
        """Fetch data from this data source.
        
        Note: This is a placeholder - the implementation will be in the concrete classes.
        """
        raise NotImplementedError("This method should be implemented by subclasses") 
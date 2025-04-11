from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.shared.infrastructure.models import MetricModel, AlertModel

class MonitoringRepository(ABC):
    @abstractmethod
    async def save_metric(self, name: str, value: float, unit: str, 
                         timestamp: datetime = None, metadata: Dict[str, Any] = None) -> MetricModel:
        """Save a new metric to the database"""
        pass

    @abstractmethod
    async def get_latest_metrics(self, names: List[str] = None, limit: int = 10) -> List[MetricModel]:
        """Get the latest metrics, optionally filtered by name"""
        pass

    @abstractmethod
    async def get_metrics_by_timerange(self, start_time: datetime, end_time: datetime, 
                                     names: List[str] = None) -> List[MetricModel]:
        """Get metrics within a specific time range"""
        pass

    @abstractmethod
    async def get_metric_average(self, name: str, hours: int = 24) -> Optional[float]:
        """Get the average value of a metric over the specified time period"""
        pass

    @abstractmethod
    async def save_alert(self, name: str, description: str, severity: str, 
                        source: str, details: Dict[str, Any] = None) -> AlertModel:
        """Save a new alert to the database"""
        pass

    @abstractmethod
    async def get_active_alerts(self) -> List[AlertModel]:
        """Get all active alerts"""
        pass

    @abstractmethod
    async def cleanup_old_metrics(self, days: int = 30) -> int:
        """Delete metrics older than the specified number of days"""
        pass 
from domain.monitoring.repositories.monitoring_repository import MonitoringRepository
from domain.monitoring.models.metric import Metric
from domain.monitoring.models.alert import Alert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from infrastructure.database.models import MetricModel, AlertModel
from typing import List, Optional
from datetime import datetime, timedelta

class MonitoringRepositoryImpl(MonitoringRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === Metrics Methods ===
    
    async def save_metric(self, metric: Metric) -> None:
        """Save a new metric to the database"""
        db_metric = MetricModel(
            name=metric.name,
            value=metric.value,
            unit=metric.unit,
            timestamp=metric.timestamp,
            extra_data=metric.metadata
        )
        self.session.add(db_metric)
        await self.session.commit()
    
    async def get_latest_metrics(self, names: List[str] = None, limit: int = 10) -> List[Metric]:
        """Get the latest metrics, optionally filtered by name"""
        query = select(MetricModel).order_by(desc(MetricModel.timestamp))
        
        if names:
            query = query.where(MetricModel.name.in_(names))
            
        query = query.limit(limit)
        result = await self.session.execute(query)
        db_metrics = result.scalars().all()
        
        return [
            Metric(
                name=m.name,
                value=m.value,
                unit=m.unit,
                timestamp=m.timestamp,
                metadata=m.extra_data
            ) for m in db_metrics
        ]
    
    async def get_metrics_by_timerange(self, start_time: datetime, end_time: datetime, 
                                      names: List[str] = None) -> List[Metric]:
        """Get metrics within a specific time range"""
        query = select(MetricModel).where(
            and_(
                MetricModel.timestamp >= start_time,
                MetricModel.timestamp <= end_time
            )
        ).order_by(desc(MetricModel.timestamp))
        
        if names:
            query = query.where(MetricModel.name.in_(names))
            
        result = await self.session.execute(query)
        db_metrics = result.scalars().all()
        
        return [
            Metric(
                name=m.name,
                value=m.value,
                unit=m.unit,
                timestamp=m.timestamp,
                metadata=m.extra_data
            ) for m in db_metrics
        ]
    
    async def get_metric_average(self, name: str, hours: int = 24) -> Optional[float]:
        """Get the average value of a metric over the specified time period"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        query = select(func.avg(MetricModel.value)).where(
            and_(
                MetricModel.name == name,
                MetricModel.timestamp >= start_time,
                MetricModel.timestamp <= end_time
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    # === Alert Methods ===
    
    async def save_alert(self, alert: Alert) -> None:
        """Save a new alert to the database"""
        db_alert = AlertModel(
            name=alert.name,
            description=alert.description,
            severity=alert.severity,
            status=alert.status,
            source=alert.source,
            timestamp=alert.timestamp,
            details=alert.details
        )
        self.session.add(db_alert)
        await self.session.commit()
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        query = select(AlertModel).where(
            AlertModel.status == 'active'
        ).order_by(desc(AlertModel.timestamp))
        
        result = await self.session.execute(query)
        db_alerts = result.scalars().all()
        
        return [
            Alert(
                name=a.name,
                description=a.description,
                severity=a.severity,
                status=a.status,
                source=a.source,
                timestamp=a.timestamp,
                details=a.details
            ) for a in db_alerts
        ]
    
    async def acknowledge_alert(self, alert_id: int, user_id: str) -> Optional[Alert]:
        """Mark an alert as acknowledged"""
        query = select(AlertModel).where(AlertModel.id == alert_id)
        result = await self.session.execute(query)
        db_alert = result.scalar_one_or_none()
        
        if not db_alert:
            return None
        
        db_alert.status = 'acknowledged'
        db_alert.acknowledged_at = datetime.utcnow()
        db_alert.acknowledged_by = user_id
        
        self.session.add(db_alert)
        await self.session.commit()
        
        return Alert(
            name=db_alert.name,
            description=db_alert.description,
            severity=db_alert.severity,
            status=db_alert.status,
            source=db_alert.source,
            timestamp=db_alert.timestamp,
            details=db_alert.details
        )
    
    async def resolve_alert(self, alert_id: int) -> Optional[Alert]:
        """Mark an alert as resolved"""
        query = select(AlertModel).where(AlertModel.id == alert_id)
        result = await self.session.execute(query)
        db_alert = result.scalar_one_or_none()
        
        if not db_alert:
            return None
        
        db_alert.status = 'resolved'
        db_alert.resolved_at = datetime.utcnow()
        
        self.session.add(db_alert)
        await self.session.commit()
        
        return Alert(
            name=db_alert.name,
            description=db_alert.description,
            severity=db_alert.severity,
            status=db_alert.status,
            source=db_alert.source,
            timestamp=db_alert.timestamp,
            details=db_alert.details
        )
    
    async def cleanup_old_metrics(self, days: int = 30) -> int:
        """Delete metrics older than the specified number of days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = select(MetricModel).where(MetricModel.timestamp < cutoff_date)
        
        result = await self.session.execute(query)
        old_metrics = result.scalars().all()
        
        count = len(old_metrics)
        for metric in old_metrics:
            await self.session.delete(metric)
        
        await self.session.commit()
        return count
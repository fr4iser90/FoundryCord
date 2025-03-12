from app.bot.domain.monitoring.repositories.monitoring_repository import MonitoringRepository
from app.bot.domain.monitoring.models.metric import Metric
from app.bot.domain.monitoring.models.alert import Alert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.bot.infrastructure.database.models import MetricModel, AlertModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class MonitoringRepositoryImpl(MonitoringRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === _LIST Methods - Return List of Objects ===
    
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
    
    async def get_latest_metrics_list(self, names: List[str] = None, limit: int = 10) -> List[Metric]:
        """_LIST: Get the latest metrics, optionally filtered by name"""
        query = select(MetricModel).order_by(desc(MetricModel.timestamp))
        
        if names:
            query = query.where(MetricModel.name.in_(names))
            
        query = query.limit(limit)
        result = await self.session.execute(query)
        db_metrics = result.scalars().all()
        
        # Return as a list of Metric objects
        return [
            Metric(
                name=m.name,
                value=m.value,
                unit=m.unit,
                timestamp=m.timestamp,
                metadata=m.extra_data or {}  # Ensure metadata is always a dict
            ) for m in db_metrics
        ]
    
    async def get_metrics_by_timerange_list(self, start_time: datetime, end_time: datetime, 
                                      names: List[str] = None) -> List[Metric]:
        """_LIST: Get metrics within a specific time range"""
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
    
    async def get_active_alerts_list(self) -> List[Alert]:
        """_LIST: Get all active alerts"""
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
    
    # === _DICT Methods - Return Dictionaries ===
    
    async def get_latest_system_metrics_dict(self) -> Dict[str, Any]:
        """_DICT: Get the latest system metrics as a dictionary grouped by category"""
        # Get all system metrics
        metrics = await self.get_latest_metrics_list(limit=100)
        
        # Transform list of metrics into structured dictionary
        result = {}
        
        for metric in metrics:
            # Extract category from metric name (e.g., "cpu.usage" -> "cpu")
            parts = metric.name.split('.')
            category = parts[0]
            
            # Create category dictionary if it doesn't exist
            if category not in result:
                result[category] = {}
            
            # For metrics with subcategories (e.g., cpu.usage)
            if len(parts) > 1:
                subcategory = parts[1]
                if category not in result:
                    result[category] = {}
                result[category][subcategory] = metric.value
            else:
                # For metrics without subcategories
                result[category] = metric.value
            
        # Ensure all expected categories exist
        for category in ['cpu', 'memory', 'disk', 'network']:
            if category not in result:
                result[category] = {}
        
        return result
    
    async def get_metrics_as_dict(self) -> Dict[str, Dict[str, Any]]:
        """_DICT: Transform metrics to structured dictionary format"""
        metrics = await self.get_latest_metrics_list(limit=100)
        
        # Transform list to dictionary
        result = {}
        for metric in metrics:
            parts = metric.name.split('.')
            if len(parts) == 2:
                category, key = parts
                if category not in result:
                    result[category] = {}
                result[category][key] = metric.value
        
        return result
    
    async def get_game_servers_dict(self) -> Dict[str, Dict[str, Any]]:
        """_DICT: Get game server metrics in dictionary format"""
        # Get metrics related to game servers (filter by name pattern or metadata)
        game_metrics = await self.get_latest_metrics_list(limit=50)
        
        # Create dictionary for game servers
        game_servers = {}
        
        for metric in game_metrics:
            # Skip non-game server metrics
            if not metric.metadata or not isinstance(metric.metadata, dict) or 'game_server' not in metric.metadata:
                continue
                
            server_name = metric.metadata.get('name', 'unknown')
            if server_name not in game_servers:
                game_servers[server_name] = {
                    'name': server_name,
                    'status': 'Offline',
                    'ports': [],
                    'online': False
                }
                
            # Update server info based on metric name
            if metric.name == 'server.status':
                game_servers[server_name]['status'] = metric.value
                game_servers[server_name]['online'] = 'online' in str(metric.value).lower() or '✅' in str(metric.value)
            elif metric.name == 'server.ports':
                # Ensure ports are parsed correctly - might be a string or list
                if isinstance(metric.value, list):
                    game_servers[server_name]['ports'] = metric.value
                elif isinstance(metric.value, str):
                    try:
                        ports = [int(p.strip()) for p in metric.value.split(',') if p.strip().isdigit()]
                        game_servers[server_name]['ports'] = ports
                    except (ValueError, AttributeError):
                        game_servers[server_name]['ports'] = []
                else:
                    game_servers[server_name]['ports'] = []
        
        return game_servers
    
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
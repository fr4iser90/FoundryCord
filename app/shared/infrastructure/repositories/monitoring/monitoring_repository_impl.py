from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.shared.infrastructure.models import MetricModel, AlertModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class MonitoringRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === Metric Methods ===
    
    async def save_metric(self, name: str, value: float, unit: str, 
                          timestamp: datetime = None, metadata: Dict[str, Any] = None) -> MetricModel:
        """Save a new metric to the database"""
        db_metric = MetricModel(
            name=name,
            value=value,
            unit=unit,
            timestamp=timestamp or datetime.utcnow(),
            extra_data=metadata or {}
        )
        self.session.add(db_metric)
        await self.session.commit()
        return db_metric
    
    async def get_latest_metrics(self, names: List[str] = None, limit: int = 10) -> List[MetricModel]:
        """Get the latest metrics, optionally filtered by name"""
        query = select(MetricModel).order_by(desc(MetricModel.timestamp))
        
        if names:
            query = query.where(MetricModel.name.in_(names))
            
        query = query.limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_metrics_by_timerange(self, start_time: datetime, end_time: datetime, 
                                      names: List[str] = None) -> List[MetricModel]:
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
        return result.scalars().all()
    
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
    
    # === System Metrics Methods ===
    
    async def get_latest_system_metrics(self) -> Dict[str, Any]:
        """Get the latest system metrics as a dictionary grouped by category"""
        # Get all system metrics
        result = await self.session.execute(
            select(MetricModel).order_by(desc(MetricModel.timestamp)).limit(100)
        )
        metrics = result.scalars().all()
        
        # Transform list of metrics into structured dictionary
        result_dict = {}
        
        for metric in metrics:
            # Extract category from metric name (e.g., "cpu.usage" -> "cpu")
            parts = metric.name.split('.')
            category = parts[0]
            
            # Create category dictionary if it doesn't exist
            if category not in result_dict:
                result_dict[category] = {}
            
            # For metrics with subcategories (e.g., cpu.usage)
            if len(parts) > 1:
                subcategory = parts[1]
                if category not in result_dict:
                    result_dict[category] = {}
                result_dict[category][subcategory] = metric.value
            else:
                # For metrics without subcategories
                result_dict[category] = metric.value
            
        # Ensure all expected categories exist
        for category in ['cpu', 'memory', 'disk', 'network']:
            if category not in result_dict:
                result_dict[category] = {}
        
        return result_dict
    
    async def get_metrics_as_dict(self) -> Dict[str, Dict[str, Any]]:
        """Transform metrics to structured dictionary format"""
        result = await self.session.execute(
            select(MetricModel).order_by(desc(MetricModel.timestamp)).limit(100)
        )
        metrics = result.scalars().all()
        
        # Transform list to dictionary
        result_dict = {}
        for metric in metrics:
            parts = metric.name.split('.')
            if len(parts) == 2:
                category, key = parts
                if category not in result_dict:
                    result_dict[category] = {}
                result_dict[category][key] = metric.value
        
        return result_dict
    
    async def get_game_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get game server metrics in dictionary format"""
        # Get metrics related to game servers
        result = await self.session.execute(
            select(MetricModel).order_by(desc(MetricModel.timestamp)).limit(50)
        )
        game_metrics = result.scalars().all()
        
        # Create dictionary for game servers
        game_servers = {}
        
        for metric in game_metrics:
            # Skip non-game server metrics
            if not metric.extra_data or not isinstance(metric.extra_data, dict) or 'game_server' not in metric.extra_data:
                continue
                
            server_name = metric.extra_data.get('name', 'unknown')
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
    
    async def save_alert(self, name: str, description: str, severity: str, 
                         source: str, details: Dict[str, Any] = None) -> AlertModel:
        """Save a new alert to the database"""
        alert = AlertModel(
            name=name,
            description=description,
            severity=severity,
            status='active',
            source=source,
            timestamp=datetime.utcnow(),
            details=details or {}
        )
        self.session.add(alert)
        await self.session.commit()
        return alert
    
    async def get_active_alerts(self) -> List[AlertModel]:
        """Get all active alerts"""
        query = select(AlertModel).where(
            AlertModel.status == 'active'
        ).order_by(desc(AlertModel.timestamp))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def acknowledge_alert(self, alert_id: int, user_id: str) -> Optional[AlertModel]:
        """Mark an alert as acknowledged"""
        query = select(AlertModel).where(AlertModel.id == alert_id)
        result = await self.session.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        alert.status = 'acknowledged'
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        
        self.session.add(alert)
        await self.session.commit()
        return alert
    
    async def resolve_alert(self, alert_id: int) -> Optional[AlertModel]:
        """Mark an alert as resolved"""
        query = select(AlertModel).where(AlertModel.id == alert_id)
        result = await self.session.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        alert.status = 'resolved'
        alert.resolved_at = datetime.utcnow()
        
        self.session.add(alert)
        await self.session.commit()
        return alert
    
    # === Cleanup Methods ===
    
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
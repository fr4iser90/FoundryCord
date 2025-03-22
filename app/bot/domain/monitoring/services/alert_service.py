from app.shared.infrastructure.models import MetricModel, AlertModel
from ..repositories.monitoring_repository import MonitoringRepository

class AlertService:
    def __init__(self, repository: MonitoringRepository):
        self.repository = repository
        self.thresholds = {
            "cpu_usage": 90,  # 90% CPU is critical
            "memory_percent": 90,  # 90% memory usage is critical
            "disk_percent": 90,  # 90% disk usage is critical
        }
        
    async def check_metrics_for_alerts(self, metrics):
        """Check metrics against thresholds and create alerts if needed"""
        alerts = []
        for metric in metrics:
            if metric.name in self.thresholds and metric.value > self.thresholds[metric.name]:
                alert = Alert(
                    metric=metric,
                    message=f"{metric.name} exceeds threshold: {metric.value}{metric.unit}",
                    severity="critical"
                )
                await self.repository.save_alert(alert)
                alerts.append(alert)
        return alerts
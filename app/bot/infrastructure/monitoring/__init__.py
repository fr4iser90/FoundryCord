from .collectors.service.impl import ServiceCollector
from .collectors.system.impl import SystemCollector

# Create instances
service_collector = ServiceCollector()
system_collector = SystemCollector()

__all__ = ['service_collector', 'system_collector']
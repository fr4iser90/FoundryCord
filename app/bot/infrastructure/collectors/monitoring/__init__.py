from infrastructure.collectors.monitoring.service.service_collector_impl import collect_all as service_collect_all
from infrastructure.collectors.monitoring.system.system_collector_impl import collect_all as system_collect_all

# Create service_collector and system_collector objects with collect_all methods
# This makes them compatible with existing code
service_collector = type('ServiceCollector', (), {'collect_all': service_collect_all})()
system_collector = type('SystemCollector', (), {'collect_all': system_collect_all})()

__all__ = [
    'service_collector',
    'system_collector'
]
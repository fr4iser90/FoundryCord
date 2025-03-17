"""System metrics data source for dashboards."""
from typing import Dict, Any, Optional
import psutil
import platform
import socket
import asyncio
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class SystemMetricsDataSource:
    """Data source for system performance metrics."""
    
    def __init__(self, bot, config: Dict[str, Any] = None):
        self.bot = bot
        self.config = config or {}
        self.cache = {}
        self.cache_timestamp = None
        self.cache_ttl = config.get('cache_ttl', 60) if config else 60  # Default 60 seconds
        
    async def fetch_data(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch system metrics data."""
        try:
            params = params or {}
            
            # Check cache
            if self.cache_timestamp and (datetime.now() - self.cache_timestamp).total_seconds() < self.cache_ttl:
                return self.cache
                
            # Prepare to collect metrics
            metrics = {}
            
            # Get metrics based on requested types
            metric_types = params.get('metrics', ['cpu', 'memory', 'disk', 'network', 'system'])
            
            # Gather metrics asynchronously
            tasks = []
            if 'cpu' in metric_types:
                tasks.append(self._get_cpu_metrics())
            if 'memory' in metric_types:
                tasks.append(self._get_memory_metrics())
            if 'disk' in metric_types:
                tasks.append(self._get_disk_metrics())
            if 'network' in metric_types:
                tasks.append(self._get_network_metrics())
            if 'system' in metric_types:
                tasks.append(self._get_system_info())
                
            # Execute and gather results
            results = await asyncio.gather(*tasks)
            
            # Combine results
            for result in results:
                metrics.update(result)
                
            # Update cache
            self.cache = metrics
            self.cache_timestamp = datetime.now()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error fetching system metrics: {e}")
            return {"error": str(e)}
    
    async def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "load_avg": psutil.getloadavg()
        }
    
    async def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics."""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "memory": {
                "total": memory.total,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        }
    
    async def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk metrics."""
        disk = psutil.disk_usage('/')
        
        return {
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        }
    
    async def _get_network_metrics(self) -> Dict[str, Any]:
        """Get network metrics."""
        net_io = psutil.net_io_counters()
        
        return {
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "hostname": socket.gethostname()
            }
        }
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.now() - boot_time).total_seconds()
        
        return {
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "hostname": socket.gethostname(),
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime
            }
        } 
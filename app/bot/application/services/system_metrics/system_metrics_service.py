"""System metrics service for monitoring system performance."""
from typing import Dict, Any, Optional
import psutil
import platform
import socket
from datetime import datetime
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class SystemMetricsService:
    """Service for collecting system performance metrics."""
    
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.cache_timestamp = None
        self.cache_ttl = 60  # Cache TTL in seconds
        self.initialized = False
        
    async def initialize(self):
        """Initialize the system metrics service."""
        try:
            # Perform initial metrics collection
            await self.collect_metrics()
            
            self.initialized = True
            logger.info("System metrics service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing system metrics service: {e}")
            return False
    
    async def collect_metrics(self):
        """Collect system metrics."""
        try:
            # Check if cache is valid
            now = datetime.now()
            if (self.cache_timestamp and 
                (now - self.cache_timestamp).total_seconds() < self.cache_ttl and 
                self.cache):
                logger.debug("Using cached system metrics")
                return self.cache
                
            # Collect metrics in separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            metrics = await loop.run_in_executor(None, self._collect_metrics_sync)
            
            # Update cache
            self.cache = metrics
            self.cache_timestamp = now
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def _collect_metrics_sync(self):
        """Collect system metrics synchronously."""
        metrics = {}
        
        # Collect CPU metrics
        metrics['cpu'] = {
            'percent': psutil.cpu_percent(interval=0.5),
            'count': psutil.cpu_count(),
            'logical_count': psutil.cpu_count(logical=True)
        }
        
        # Collect memory metrics
        memory = psutil.virtual_memory()
        metrics['memory'] = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
        
        # Collect disk metrics
        disk = psutil.disk_usage('/')
        metrics['disk'] = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
        
        # Collect network metrics
        net_io = psutil.net_io_counters()
        metrics['network'] = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'hostname': socket.gethostname()
        }
        
        # Collect system info
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.now() - boot_time).total_seconds()
        metrics['system'] = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
            'boot_time': boot_time.isoformat(),
            'uptime_seconds': uptime
        }
        
        return metrics
    
    async def get_metrics(self, metric_types=None):
        """Get system metrics, optionally filtered by type."""
        metrics = await self.collect_metrics()
        
        if not metric_types:
            return metrics
            
        # Filter metrics by type
        if isinstance(metric_types, str):
            metric_types = [metric_types]
            
        filtered_metrics = {}
        for metric_type in metric_types:
            if metric_type in metrics:
                filtered_metrics[metric_type] = metrics[metric_type]
                
        return filtered_metrics
    
    async def cleanup(self):
        """Clean up system metrics service resources."""
        logger.info("System metrics service cleaned up")
        return True 
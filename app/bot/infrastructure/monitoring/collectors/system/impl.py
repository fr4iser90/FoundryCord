import asyncio
import logging
import os
import psutil
import platform
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from app.shared.infrastructure.models import MetricModel
from app.shared.domain.monitoring.collectors import SystemCollectorInterface
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from .components.base import collect_system_data

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

class SystemCollector(SystemCollectorInterface):
    async def collect_all(self) -> List[MetricModel]:
        """Implements the base collect_all method"""
        return await self.collect_system_metrics()
        
    async def collect_system_metrics(self) -> List[MetricModel]:
        """Converts system data into MetricModel objects"""
        logger.info("Collecting system metrics...")
        
        # Get raw data from your existing collector
        data = await collect_system_data()
        
        # Convert to metrics
        metrics = []
        
        # --- System Info --- 
        # Hostname (Using platform.node() for consistency)
        hostname = platform.node() 
        metrics.append(MetricModel(
            name="hostname",
            value=0.0, # Dummy float value
            unit=None,
            metric_data={"type": "system", "component": "system", "hostname": hostname}
        ))
        
        # Platform (From collected data or platform module)
        platform_name = data.get('platform', platform.system())
        metrics.append(MetricModel(
            name="platform",
            value=0.0, # Dummy float value
            unit=None,
            metric_data={"type": "system", "component": "system", "platform": platform_name}
        ))
        
        # Uptime (From collected data)
        uptime_str = data.get('uptime', "N/A")
        metrics.append(MetricModel(
            name="uptime",
            value=0.0, # Dummy float value
            unit=None,
            metric_data={"type": "system", "component": "system", "uptime": uptime_str}
        ))
        # --- End System Info ---
        
        # CPU metrics
        metrics.append(MetricModel(
            name="cpu_usage",
            value=data['cpu'],
            unit="percent",
            metric_data={"type": "system", "component": "cpu"}
        ))
        
        # Add CPU hardware information from hardware_info
        if isinstance(data.get('hardware_info', {}), dict):
            # CPU model
            if 'cpu_model' in data['hardware_info']:
                metrics.append(MetricModel(
                    name="cpu_model",
                    value=0.0, # Store float value?
                    unit=None,
                    metric_data={"type": "system", "component": "cpu", "model_name": data['hardware_info']['cpu_model']} # Keep JSON for structured data
                ))
            
            # CPU cores
            if 'cpu_cores' in data['hardware_info']:
                metrics.append(MetricModel(
                    name="cpu_cores",
                    value=data['hardware_info']['cpu_cores'],
                    unit="count",
                    metric_data={"type": "system", "component": "cpu"}
                ))
            
            # CPU threads
            if 'cpu_threads' in data['hardware_info']:
                metrics.append(MetricModel(
                    name="cpu_threads",
                    value=data['hardware_info']['cpu_threads'],
                    unit="count",
                    metric_data={"type": "system", "component": "cpu"}
                ))
        
        # Memory metrics
        memory = data['memory']
        metrics.append(MetricModel(
            name="memory_used",
            value=memory.used,
            unit="bytes",
            metric_data={"type": "system", "component": "memory"}
        ))
        metrics.append(MetricModel(
            name="memory_total",
            value=memory.total,
            unit="bytes",
            metric_data={"type": "system", "component": "memory"}
        ))
        metrics.append(MetricModel(
            name="memory_percent",
            value=memory.percent,
            unit="percent",
            metric_data={"type": "system", "component": "memory"}
        ))
        
        # Swap metrics
        swap = data['swap']
        metrics.append(MetricModel(
            name="swap_used",
            value=swap.used,
            unit="bytes",
            metric_data={"type": "system", "component": "memory"}
        ))
        metrics.append(MetricModel(
            name="swap_total",
            value=swap.total,
            unit="bytes",
            metric_data={"type": "system", "component": "memory"}
        ))
        
        # Disk metrics
        disk = data['disk']
        metrics.append(MetricModel(
            name="disk_percent",
            value=disk.percent,
            unit="percent",
            metric_data={"type": "system", "component": "storage", "path": "/"}
        ))
        
        # Festplatten-Metriken
        if isinstance(data['disk_details'], dict) and data['disk_details']:
            # Prüfen ob Root-Partition vorhanden ist
            if '/' in data['disk_details']:
                root_path = '/'
            # Alternativ die erste verfügbare Partition nehmen
            elif data['disk_details']:
                root_path = next(iter(data['disk_details']))
            else:
                root_path = None
            
            # Wenn ein gültiger Pfad gefunden wurde
            if root_path:
                details = data['disk_details'][root_path]
                # Disk-Free Metrik
                metrics.append(MetricModel(
                    name="disk_free",
                    value=details["total"] - details["used"],
                    unit="bytes",
                    metric_data={"type": "system", "component": "storage"}
                ))
                
                # Disk-Total Metrik
                metrics.append(MetricModel(
                    name="disk_total",
                    value=details["total"],
                    unit="bytes",
                    metric_data={"type": "system", "component": "storage"}
                ))
            
            # Wenn keine Festplatte gefunden wurde, Basis-Disk-Info verwenden
            else:
                # Fallback auf die Basis-Disk-Info
                if isinstance(data.get('disk'), psutil._common.sdiskusage):
                    metrics.append(MetricModel(
                        name="disk_free",
                        value=data['disk'].free,
                        unit="bytes",
                        metric_data={"type": "system", "component": "storage"}
                    ))
                    metrics.append(MetricModel(
                        name="disk_total",
                        value=data['disk'].total,
                        unit="bytes",
                        metric_data={"type": "system", "component": "storage"}
                    ))
        
        # Netzwerk-Metriken
        if isinstance(data['network_stats'], dict):
            metrics.append(MetricModel(
                name="net_upload",
                value=round(data['network_stats'].get('net_upload', 0), 1),
                unit="mbps",
                metric_data={"type": "system", "component": "network"}
            ))
            metrics.append(MetricModel(
                name="net_download",
                value=round(data['network_stats'].get('net_download', 0), 1),
                unit="mbps",
                metric_data={"type": "system", "component": "network"}
            ))
        logger.info(f"Collected {len(metrics)} system metrics")
        return metrics



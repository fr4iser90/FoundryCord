import asyncio
import logging
from typing import List

from ..models.metric import Metric
from .service_collector.docker import get_docker_status
from .service_collector.security import get_ssh_attempts
from .service_collector.services import check_services_status
from .service_collector.base import collect_service_data

logger = logging.getLogger('homelab_bot')

async def collect_all() -> List[Metric]:
    """Collects service metrics and returns them as a list of Metric objects"""
    logger.info("Collecting service metrics...")
    
    # Get raw data from your service collector
    data = await collect_service_data()
    
    metrics = []
    
    # Use data to create metrics
    # ... process docker_running, docker_errors, docker_details from data
    # ... process ssh_attempts, last_ssh_ip from data
    # ... process services from data
    
    # Collect service data in parallel
    tasks = [
        get_docker_status(),
        get_ssh_attempts(),
        check_services_status(include_private=False)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process Docker status
    if not isinstance(results[0], Exception):
        docker_running, docker_errors, docker_details = results[0]
        
        if isinstance(docker_running, int):
            metrics.append(Metric(
                name="docker_running",
                value=docker_running,
                unit="count",
                metadata={"type": "service", "component": "docker"}
            ))
        
        if isinstance(docker_errors, int):
            metrics.append(Metric(
                name="docker_errors",
                value=docker_errors,
                unit="count",
                metadata={"type": "service", "component": "docker"}
            ))
        
        # Process container details
        if isinstance(docker_details, str):
            for line in docker_details.strip().split("\n"):
                if ": " in line:
                    container_name, status = line.split(": ", 1)
                    metrics.append(Metric(
                        name="container_status",
                        value=1 if "Running" in status or "Up" in status else 0,
                        unit="status",
                        metadata={
                            "type": "service", 
                            "component": "docker",
                            "container": container_name,
                            "status_text": status
                        }
                    ))
    
    # Process SSH attempts
    if not isinstance(results[1], Exception):
        ssh_attempts, last_ssh_ip = results[1]
        
        if ssh_attempts not in ("N/A", "N/A (nur Linux)"):
            try:
                ssh_attempts_val = int(ssh_attempts)
                metrics.append(Metric(
                    name="ssh_attempts",
                    value=ssh_attempts_val,
                    unit="count",
                    metadata={
                        "type": "service", 
                        "component": "security",
                        "last_ip": last_ssh_ip
                    }
                ))
            except (ValueError, TypeError):
                pass
    
    # Process service status checks
    if not isinstance(results[2], Exception) and isinstance(results[2], dict):
        service_status = results[2]
        
        for service_name, status in service_status.items():
            metrics.append(Metric(
                name="service_status",
                value=1 if any(x in status for x in ["Online", "✅", "✓"]) else 0,
                unit="status",
                metadata={
                    "type": "service",
                    "service_name": service_name,
                    "status_text": status
                }
            ))
    
    logger.info(f"Collected {len(metrics)} service metrics")
    return metrics
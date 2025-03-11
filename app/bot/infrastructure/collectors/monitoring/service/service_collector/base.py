import asyncio
import logging

from .docker import get_docker_status
from .security import get_ssh_attempts
from .services import check_services_status

logger = logging.getLogger('homelab_bot')

async def collect_service_data():
    """Sammelt alle Service-Daten und gibt sie als Dictionary zurück"""
    logger.info("Sammle Service-Daten...")
    
    data = {}
    
    # Service-Daten parallel sammeln
    tasks = [
        get_docker_status(),
        get_ssh_attempts(),
        check_services_status(include_private=False)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Ergebnisse dem Daten-Dictionary hinzufügen
    if not isinstance(results[0], Exception):
        data['docker_running'], data['docker_errors'], data['docker_details'] = results[0]
    else:
        data['docker_running'], data['docker_errors'], data['docker_details'] = "N/A", "N/A", "Docker nicht verfügbar"
    
    if not isinstance(results[1], Exception):
        data['ssh_attempts'], data['last_ssh_ip'] = results[1]
    else:
        data['ssh_attempts'], data['last_ssh_ip'] = "N/A", "N/A"
    
    data['services'] = results[2] if not isinstance(results[2], Exception) else {}
    
    return data
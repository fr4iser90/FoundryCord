import asyncio
import logging
import os
import psutil
import platform
from dotenv import load_dotenv

from .docker import get_docker_status
from .network import fetch_public_ip, get_network_stats
from .security import get_ssh_attempts
from .services import check_services_status
from .storage import get_disk_usage_all
from .system import get_system_uptime, get_cpu_temperature
from .hardware import get_hardware_info

logger = logging.getLogger('homelab_bot')

load_dotenv()
DOMAIN = os.getenv('DOMAIN')

async def collect_system_data():
    """Sammelt alle Systemdaten und gibt sie als Dictionary zurück"""
    logger.info("Sammle Systemdaten...")
    
    data = {}
    
    # Basis-Systemdaten
    data['cpu'] = psutil.cpu_percent(interval=1)
    data['memory'] = psutil.virtual_memory()
    data['swap'] = psutil.swap_memory()
    data['disk'] = psutil.disk_usage('/')
    data['platform'] = platform.system()
    data['release'] = platform.release()
    data['domain'] = DOMAIN
    
    logger.info("Basis-Systemdaten gesammelt, sammle erweiterte Daten...")
    
    # Erweiterte Daten parallel sammeln
    tasks = [
        fetch_public_ip(),
        get_system_uptime(),
        get_cpu_temperature(),
        get_docker_status(),
        get_network_stats(),
        get_ssh_attempts(),
        check_services_status(),
        get_disk_usage_all(),
        get_hardware_info()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Ergebnisse dem Daten-Dictionary hinzufügen
    data['public_ip'] = results[0] if not isinstance(results[0], Exception) else "N/A"
    data['uptime'] = results[1] if not isinstance(results[1], Exception) else "N/A"
    data['cpu_temp'] = results[2] if not isinstance(results[2], Exception) else "N/A"
    
    if not isinstance(results[3], Exception):
        data['docker_running'], data['docker_errors'], data['docker_details'] = results[3]
    else:
        data['docker_running'], data['docker_errors'], data['docker_details'] = "N/A", "N/A", "Docker nicht verfügbar"
    
    if not isinstance(results[4], Exception):
        data['net_admin'], data['net_public'] = results[4]
    else:
        data['net_admin'], data['net_public'] = "N/A", "N/A"
    
    if not isinstance(results[5], Exception):
        data['ssh_attempts'], data['last_ssh_ip'] = results[5]
    else:
        data['ssh_attempts'], data['last_ssh_ip'] = "N/A", "N/A"
    
    data['services'] = results[6] if not isinstance(results[6], Exception) else {}
    data['disk_details'] = results[7] if not isinstance(results[7], Exception) else "Keine Festplatten gefunden"
    
    return data
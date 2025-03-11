import asyncio
import logging
import os
import psutil
import platform
from dotenv import load_dotenv

from .network import fetch_public_ip, get_network_stats
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
        get_network_stats(),
        get_disk_usage_all(),
        get_hardware_info()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Ergebnisse dem Daten-Dictionary hinzufügen
    data['public_ip'] = results[0] if not isinstance(results[0], Exception) else "N/A"
    data['uptime'] = results[1] if not isinstance(results[1], Exception) else "N/A"
    data['cpu_temp'] = results[2] if not isinstance(results[2], Exception) else "N/A"
    
    if not isinstance(results[3], Exception):
        network_data = results[3]
        if isinstance(network_data, dict):
            data['network_stats'] = network_data
        else:
            # Alte Formatierung (Tupel)
            data['net_admin'], data['net_public'] = network_data
    else:
        data['network_stats'] = {}
        data['net_admin'], data['net_public'] = "N/A", "N/A"
    
    data['disk_details'] = results[4] if not isinstance(results[4], Exception) else "Keine Festplatten gefunden"
    data['hardware_info'] = results[5] if not isinstance(results[5], Exception) else {}
    
    return data
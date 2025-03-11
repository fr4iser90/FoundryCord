import psutil
import cpuinfo
import logging
from typing import Dict, Any
import platform

logger = logging.getLogger('homelab_bot')

async def get_cpu_info() -> Dict[str, Any]:
    """Sammelt CPU-spezifische Informationen"""
    try:
        cpu_info = {}
        
        # Detaillierte CPU Info
        try:
            info = cpuinfo.get_cpu_info()
            cpu_info['cpu_model'] = info.get('brand_raw', 'Unbekannt')
            logger.debug(f"CPU Info erfolgreich gelesen: {info.get('brand_raw')}")
        except Exception as e:
            logger.error(f"Fehler beim Lesen der CPU Info via cpuinfo: {e}")
            try:
                cpu_info['cpu_model'] = platform.processor()
                logger.debug(f"CPU Info via platform erfolgreich gelesen: {platform.processor()}")
            except Exception as e:
                logger.error(f"Fehler beim Lesen der CPU Info via platform: {e}")
                cpu_info['cpu_model'] = "Unbekannt"
        
        # Kerne und Threads
        cpu_info['cpu_cores'] = psutil.cpu_count(logical=False)
        cpu_info['cpu_threads'] = psutil.cpu_count(logical=True)
        
        # CPU Frequenz
        freq = psutil.cpu_freq()
        if freq:
            cpu_info['cpu_freq_current'] = f"{freq.current/1000:.2f} GHz"
            cpu_info['cpu_freq_min'] = f"{freq.min/1000:.2f} GHz"
            cpu_info['cpu_freq_max'] = f"{freq.max/1000:.2f} GHz"
        
        logger.debug(f"Gesammelte CPU Informationen: {cpu_info}")
        return cpu_info
    except Exception as e:
        logger.error(f"Kritischer Fehler in get_cpu_info: {e}")
        return {
            'cpu_model': "Nicht verfügbar",
            'cpu_cores': "N/A",
            'cpu_threads': "N/A"
        }
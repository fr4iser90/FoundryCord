import platform
import psutil
import logging
from typing import Dict, Any
import cpuinfo

logger = logging.getLogger('homelab_bot')

async def get_hardware_info() -> Dict[str, Any]:
    """Sammelt umfassende Hardware-Informationen mit Python-Bibliotheken"""
    try:
        hardware_info = {}
        
        # CPU Informationen mit py-cpuinfo
        try:
            cpu_info = cpuinfo.get_cpu_info()
            hardware_info['cpu_model'] = cpu_info.get('brand_raw', 'Unbekannt')
        except Exception as e:
            logger.debug(f"CPU Info Fehler: {e}")
            hardware_info['cpu_model'] = platform.processor() or "Unbekannt"
        
        hardware_info['cpu_cores'] = psutil.cpu_count(logical=False)
        hardware_info['cpu_threads'] = psutil.cpu_count(logical=True)
        
        # CPU Frequenz
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            hardware_info['cpu_freq_current'] = f"{cpu_freq.current/1000:.2f} GHz"
            hardware_info['cpu_freq_min'] = f"{cpu_freq.min/1000:.2f} GHz"
            hardware_info['cpu_freq_max'] = f"{cpu_freq.max/1000:.2f} GHz"
        
        # RAM Informationen
        memory = psutil.virtual_memory()
        hardware_info['ram_total'] = memory.total / (1024**3)  # GB
        
        # System Informationen
        hardware_info['system_platform'] = platform.platform()
        
        # Netzwerk-Interfaces
        network_info = []
        for interface, stats in psutil.net_if_stats().items():
            if stats.isup:  # Nur aktive Interfaces
                speed = f"{stats.speed}Mb/s" if stats.speed > 0 else "Unbekannt"
                network_info.append(f"{interface} (Speed: {speed})")
        hardware_info['network_adapters'] = "\n".join(network_info) if network_info else "Keine aktiven Netzwerk-Adapter"
        
        return hardware_info

    except Exception as e:
        logger.error(f"Fehler beim Sammeln der Hardware-Informationen: {e}")
        return {
            'cpu_model': "Nicht verfügbar",
            'cpu_cores': "N/A",
            'cpu_threads': "N/A",
            'ram_total': 0,  # Numerischer Wert
            'error': str(e)
        }
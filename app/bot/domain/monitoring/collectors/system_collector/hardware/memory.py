import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger('homelab_bot')

async def get_memory_info() -> Dict[str, Any]:
    """Sammelt RAM-spezifische Informationen"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        memory_info = {
            'ram_total': memory.total / (1024**3),  # GB
            'ram_used': memory.used / (1024**3),
            'ram_percent': memory.percent,
            'swap_total': swap.total / (1024**3),
            'swap_used': swap.used / (1024**3),
            'swap_percent': swap.percent
        }
        
        logger.debug(f"Gesammelte Memory Informationen: {memory_info}")
        return memory_info
    except Exception as e:
        logger.error(f"Fehler beim Sammeln der Memory Informationen: {e}")
        return {
            'ram_total': 0,
            'ram_used': 0,
            'ram_percent': 0,
            'swap_total': 0,
            'swap_used': 0,
            'swap_percent': 0
        }
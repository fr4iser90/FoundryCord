"""Collector for bot host system information."""
from typing import Dict, Any
import platform
import psutil
from app.shared.interface.logging.api import get_shared_logger # Use shared logger

logger = get_shared_logger()

def collect_system_info_func() -> Dict[str, Any]:
    """
    Collects system information from the bot's host.
    
    Returns:
        Dict with system information.
    """
    logger.debug("Executing bot system_info state collector...")
    try:
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "memory_total_bytes": psutil.virtual_memory().total,
            "memory_available_bytes": psutil.virtual_memory().available,
            "disk_usage_root": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }
    except Exception as e:
        logger.error(f"Error collecting bot system info: {e}", exc_info=True)
        return {"error": str(e)}

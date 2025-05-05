"""Collector for basic system information."""
from typing import Dict, Any
import platform
import psutil
from app.shared.interfaces.logging.api import get_shared_logger

logger = get_shared_logger()

async def get_system_info(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Collect system information from the host environment.
    
    Returns:
        Dict with system information
    """
    logger.debug("Executing system_info state collector...")
    try:
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "memory_total_bytes": psutil.virtual_memory().total,
            "memory_available_bytes": psutil.virtual_memory().available,
            # Add more system info if needed
        }
    except Exception as e:
        logger.error(f"Error collecting system info: {e}", exc_info=True)
        return {"error": str(e)} 
"""
State collector functions for system information.
"""
from typing import Dict, Any
import platform
import os
from app.shared.interface.logging.api import get_shared_logger

logger = get_shared_logger()

def get_system_info(context: Dict[str, Any]) -> Dict[str, Any]:
    """Collects basic OS and Python environment details."""
    logger.debug("Executing system_info state collector...")
    try:
        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "cpu_cores": os.cpu_count(),
            "cwd": os.getcwd()
            # Avoid adding overly sensitive information here
        }
    except Exception as e:
        logger.error(f"Error in system_info collector: {e}", exc_info=True)
        return {"error": str(e), "message": "Could not fetch system info."} 
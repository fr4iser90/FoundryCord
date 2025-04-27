"""Collector for bot performance metrics."""
from typing import Dict, Any
import psutil
from app.shared.interface.logging.api import get_shared_logger

logger = get_shared_logger()

def collect_performance_metrics_func() -> Dict[str, Any]:
    """
    Collects performance metrics about the current bot process.
    
    Returns:
        Dict with performance metrics.
    """
    logger.debug("Executing bot performance_metrics state collector...")
    try:
        process = psutil.Process() # Get current process
        
        mem_info = process.memory_info()
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1), # Add small interval for accuracy
            "memory_usage": {
                "rss_bytes": mem_info.rss,  # Resident Set Size
                "vms_bytes": mem_info.vms,  # Virtual Memory Size
                "percent": process.memory_percent()
            },
            "threads": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections()),
            "system_load_avg": psutil.getloadavg() # 1, 5, 15 min load avg
        }
    except Exception as e:
        logger.error(f"Error collecting bot performance metrics: {e}", exc_info=True)
        return {"error": str(e)} 
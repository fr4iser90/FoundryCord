"""Collector for database status."""
from typing import Dict, Any
from sqlalchemy import text
from app.shared.infrastructure.database.api import session_context
from app.shared.interfaces.logging.api import get_shared_logger
import time

logger = get_shared_logger()

async def get_database_status(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Checks the database connection status."""
    logger.debug("Executing database_status state collector...")
    
    start_time = time.perf_counter()
    try:
        async with session_context() as session:
            # Execute a simple query to check connectivity
            result = await session.execute(text("SELECT 1"))
            scalar_result = result.scalar_one()
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            if scalar_result == 1:
                return {
                    "status": "connected",
                    "latency_ms": round(latency_ms, 2)
                }
            else:
                 logger.warning(f"Database status check query returned unexpected result: {scalar_result}")
                 return {
                     "status": "error",
                     "error": "Unexpected query result",
                     "latency_ms": round(latency_ms, 2)
                 }
                 
    except Exception as e:
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        logger.error(f"Database connection error in state collector: {e}", exc_info=False)
        return {
            "status": "error",
            "error": str(e),
            "latency_ms": round(latency_ms, 2)
        } 
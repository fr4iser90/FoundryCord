"""Collector for database connection status from the bot's perspective."""
from typing import Dict, Any
from app.shared.interfaces.logging.api import get_shared_logger
import time

logger = get_shared_logger()

async def collect_database_connection_info_func(bot) -> Dict[str, Any]:
    """
    Collects database connection information using the bot's db_service.

    Args:
        bot: The Discord bot instance (expected to have a db_service attribute).

    Returns:
        Dict with database connection status.
    """
    logger.debug("Executing bot database_connection state collector...")
    if not bot:
        return {"status": "error", "error": "Bot instance not provided"}

    db_service = getattr(bot, 'db_service', None)
    if not db_service:
        return {"status": "unavailable", "reason": "No db_service found on bot instance"}
        
    is_connected = False
    start_time = time.perf_counter()
    try:
        # Check if we can execute a simple query via the service's ping method
        ping_result = await db_service.ping()
        is_connected = ping_result # Assume ping returns True on success
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        status = "connected" if is_connected else "disconnected"
        error_msg = None if is_connected else "Ping failed"

    except Exception as e:
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        logger.error(f"Error pinging database via bot's db_service: {e}", exc_info=False)
        status = "error"
        error_msg = str(e)
        
    # Try to get engine URL safely, redacting password
    engine_url_str = "unknown"
    try:
        if hasattr(db_service, 'engine') and hasattr(db_service.engine, 'url'):
            url = db_service.engine.url
            engine_url_str = str(url.render_as_string(hide_password=True))
    except Exception as url_err:
        logger.warning(f"Could not render database engine URL: {url_err}")

    return {
        "status": status,
        "is_connected": is_connected,
        "latency_ms": round(latency_ms, 2),
        "error": error_msg,
        "database_type": getattr(db_service, 'db_type', 'unknown'),
        "engine_url_redacted": engine_url_str
    }

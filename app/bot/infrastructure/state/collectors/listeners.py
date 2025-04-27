"""Collector for active event listeners."""
from typing import Dict, Any
import nextcord
from app.shared.interface.logging.api import get_shared_logger

logger = get_shared_logger()

def collect_active_listeners_func(bot: nextcord.Client) -> Dict[str, Any]:
    """
    Collects information about active event listeners from the bot instance.

    Args:
        bot: The Discord bot instance.

    Returns:
        Dict with event listener information.
    """
    logger.debug("Executing active_listeners state collector...")
    if not bot or not hasattr(bot, '_listeners'):
        return {"error": "Bot instance not available or listeners attribute missing"}

    try:
        listeners = {}
        total_listener_count = 0
        
        # bot._listeners maps event names (e.g., 'on_message') to lists of handlers
        for event_name, handlers in bot._listeners.items():
            if handlers: # Only include events with active handlers
                listeners[event_name] = len(handlers)
                total_listener_count += len(handlers)
            
        return {
            "event_types_with_listeners": sorted(list(listeners.keys())),
            "listener_counts_per_event": listeners,
            "total_listeners_count": total_listener_count
        }
    except Exception as e:
        logger.error(f"Error collecting active listeners: {e}", exc_info=True)
        return {"error": str(e)} 
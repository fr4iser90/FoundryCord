"""
Initializes and registers server-side state collectors.
"""
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service
from app.shared.interface.logging.api import get_shared_logger

# Import collector functions from their respective modules
# (These will be added in the next steps)
# from app.bot.state_collectors import get_bot_status_info
# from app.shared.infrastructure.system.state_collectors import get_system_info

logger = get_shared_logger()

def register_all_state_collectors():
    """Registers all known server-side state collectors by importing functions
       and calling the registration method on the snapshot service.
    """
    logger.info("Registering server-side state collectors...")
    snapshot_service = get_state_snapshot_service()

    # --- Bot Collectors --- 
    try:
        # Dynamically import or define bot collectors here
        from app.bot.infrastructure.state.collectors.bot_status import get_bot_status_info
        snapshot_service.register_collector(
            name="bot_status",
            collector_fn=get_bot_status_info,
            requires_approval=False, 
            scope="bot",
            description="Basic status information about the Discord bot (Placeholder)"
        )
    except ImportError:
        logger.warning("Bot state collectors not found or could not be imported.")
    except Exception as e:
        logger.error(f"Error registering bot_status collector: {e}", exc_info=True)

    # --- System Collectors --- 
    try:
        # Dynamically import or define system collectors here
        from app.shared.infrastructure.system.state_collectors import get_system_info
        snapshot_service.register_collector(
            name="system_info",
            collector_fn=get_system_info,
            requires_approval=False,
            scope="web", # Or 'global'
            description="Basic OS and Python environment details"
        )
    except ImportError:
        logger.warning("System state collectors not found or could not be imported.")
    except Exception as e:
        logger.error(f"Error registering system_info collector: {e}", exc_info=True)


    # --- Register other collectors here ---
    # Example:
    # try:
    #     from app.some_module.state_collectors import get_some_data
    #     snapshot_service.register_collector('some_data', get_some_data, ...)
    # except ImportError:
    #     logger.warning("SomeModule state collectors not found.")
    # except Exception as e:
    #     logger.error(f"Error registering some_data collector: {e}", exc_info=True)

    logger.info("Server-side state collectors registration process completed.") 
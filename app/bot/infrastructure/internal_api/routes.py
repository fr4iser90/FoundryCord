import asyncio
from aiohttp import web
from app.shared.interface.logging.api import get_bot_logger
# Assuming the main bot class is accessible or passed in
# from app.bot.core.main import HomelabBot 

logger = get_bot_logger()

# --- Handler for triggering Guild Approval Workflow --- 
async def handle_trigger_approve_guild(request: web.Request):
    """Handles POST /internal/trigger/approve_guild/{guild_id}"""
    guild_id = request.match_info.get('guild_id')
    response_status = 500 # Default to internal server error
    response_body = {'status': 'error', 'message': 'Internal server error'} # Default error body
    
    try:
        if not guild_id:
            logger.error("Internal API: Missing guild_id in trigger_approve_guild request")
            response_status = 400
            response_body = {'status': 'error', 'message': 'Missing guild_id'}
            return web.json_response(response_body, status=response_status)

        bot_app = request.app.get('bot_instance')
        if not bot_app or not hasattr(bot_app, 'control_service'):
            logger.error("Internal API: Bot instance or control_service not found")
            response_status = 500
            response_body = {'status': 'error', 'message': 'Internal server error: Bot not configured'}
            return web.json_response(response_body, status=response_status)

        logger.info(f"Internal API: Received request to trigger approval for guild {guild_id}")
        try:
            # Schedule the actual bot logic to run without blocking the API response
            async def run_task():
                try:
                    success = await bot_app.control_service.trigger_approve_guild(guild_id=guild_id)
                    if not success:
                        logger.error(f"Internal API: Bot reported failure processing approval for guild {guild_id} (async task)")
                    else:
                        logger.info(f"Internal API: Bot successfully processed approval for guild {guild_id} (async task)")
                except Exception as task_err:
                     logger.error(f"Internal API: Error in background approval task for guild {guild_id}: {task_err}", exc_info=True)
            
            asyncio.create_task(run_task())
            # Return 202 Accepted immediately
            response_status = 202
            response_body = {'status': 'ok', 'message': f'Approval trigger scheduled for guild {guild_id}'}
            logger.info(f"Internal API: Sending {response_status} response for trigger approve guild {guild_id}")
            return web.json_response(response_body, status=response_status)
        except Exception as e:
            logger.error(f"Internal API: Error scheduling approval task for guild {guild_id}: {e}", exc_info=True)
            response_status = 500
            response_body = {'status': 'error', 'message': 'Internal server error during task scheduling'}
            return web.json_response(response_body, status=response_status)
            
    except Exception as outer_e:
         # Catch any unexpected errors in the handler setup
         logger.error(f"Internal API: Unexpected error in handle_trigger_approve_guild for guild {guild_id or 'unknown'}: {outer_e}", exc_info=True)
         # Use default response_status (500) and response_body
         return web.json_response(response_body, status=response_status)
    finally:
        # Optional: Log the final response details regardless of success/failure
        # logger.debug(f"Internal API: Final response for trigger approve guild {guild_id or 'unknown'}: status={response_status}, body={response_body}")
        pass # Avoid redundant logging if logged before return

# --- Handler for PING --- 
async def handle_ping(request: web.Request):
    """Handles GET /internal/ping"""
    logger.debug("Internal API: Received /internal/ping request")
    response_body = {"status": "pong"}
    logger.debug("Internal API: Sending 200 response for /internal/ping")
    return web.json_response(response_body, status=200)

# --- Route Setup Function --- 
def setup_internal_routes(app: web.Application):
    """Add routes to the internal API application."""
    router = app.router
    logger.info("Setting up internal API routes...")
    router.add_post('/internal/trigger/approve_guild/{guild_id}', handle_trigger_approve_guild)
    router.add_get('/internal/ping', handle_ping)
    
    # Improved logging for routes
    route_details = []
    for route in list(router.routes()):
        if hasattr(route, 'method') and hasattr(route.resource, 'canonical'):
            route_details.append(f"  - [{route.method}] {route.resource.canonical}")
        else: # Fallback for routes without standard attributes
             route_details.append(f"  - {route}")
             
    if route_details:
        logger.info("Internal API routes added:\n" + "\n".join(route_details))
    else:
         logger.info("Internal API routes added: No routes found.") 
# app/bot/infrastructure/internal_api/server.py
import asyncio
from aiohttp import web
from app.shared.interface.logging.api import get_bot_logger
from .routes import setup_internal_routes  # Import from the routes file

logger = get_bot_logger()

# --- Request Logging Middleware --- 
@web.middleware
async def request_logger_middleware(request: web.Request, handler):
    """Logs basic information about each incoming request."""
    # Log before handling the request
    logger.info(f"Internal API: Received request - Method={request.method}, Path={request.path}, Peer={request.remote}")
    start_time = asyncio.get_event_loop().time()
    try:
        response = await handler(request)
        # Log after handling the request
        duration = (asyncio.get_event_loop().time() - start_time) * 1000 # duration in ms
        logger.info(f"Internal API: Responded to {request.method} {request.path} with status {response.status} in {duration:.2f}ms")
        return response
    except web.HTTPException as http_exc:
        # Log HTTP exceptions specifically (like 404 Not Found, 400 Bad Request, etc.)
        duration = (asyncio.get_event_loop().time() - start_time) * 1000
        logger.warning(f"Internal API: HTTP error for {request.method} {request.path} - Status={http_exc.status}, Reason={http_exc.reason} in {duration:.2f}ms")
        raise # Re-raise the exception to let aiohttp handle it
    except Exception as e:
        # Log unexpected errors during request handling
        duration = (asyncio.get_event_loop().time() - start_time) * 1000
        logger.error(f"Internal API: Unhandled exception during {request.method} {request.path} handling: {e} in {duration:.2f}ms", exc_info=True)
        # Consider returning a generic 500 response here, or re-raise
        raise # Re-raise to let default error handling occur

class InternalAPIServer:
    """Runs the internal aiohttp API server for the bot."""
    def __init__(self, bot_instance, host: str = '0.0.0.0', port: int = 9090):
        self.bot_instance = bot_instance
        self.host = host
        self.port = port
        self.runner = None
        self.site = None
        self._server_task = None # To hold the asyncio task running the server

    async def setup_server(self) -> web.Application:
        """Sets up the aiohttp application and routes."""
        # Add the logging middleware
        app = web.Application(middlewares=[request_logger_middleware])
        
        # Store the bot instance in the app context so handlers can access it
        app['bot_instance'] = self.bot_instance 
        setup_internal_routes(app) # Setup routes from routes.py - this already logs routes
        
        # No need to log routes again here as routes.py does it now.
        # logger.info(f"Internal API application configured. Routes: {list(app.router.routes())}")
        return app

    async def start(self):
        """Starts the internal API server non-blockingly."""
        if self.runner:
            logger.warning("Internal API server already running or start called multiple times.")
            return

        app = await self.setup_server()
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        
        try:
            await self.site.start()
            logger.info(f"Internal API server started successfully on http://{self.host}:{self.port}")
            # Start the server's main loop in a background task
            self._server_task = asyncio.create_task(self._run_server_loop())
        except OSError as e:
            logger.error(f"Failed to start Internal API server on {self.host}:{self.port}. Error: {e}. Might the port be in use?", exc_info=True)
            # Ensure cleanup happens if start fails
            await self.stop()
        except Exception as e:
            logger.error(f"An unexpected error occurred during Internal API server startup: {e}", exc_info=True)
            await self.stop()
            
    async def _run_server_loop(self):
        """Keeps the server running. This task runs until cancelled."""
        try:
            # This await will basically run forever until the task is cancelled
            await asyncio.Future() 
        except asyncio.CancelledError:
            logger.info("Internal API server loop cancellation requested.")
        except Exception as e:
            logger.error(f"Internal API server loop encountered an unexpected error: {e}", exc_info=True)
        finally:
            logger.info("Internal API server loop finished.")

    async def stop(self):
        """Stops the internal API server gracefully."""
        logger.info("Attempting to stop Internal API server...")
        # Cancel the server loop task first
        if self._server_task and not self._server_task.done():
            self._server_task.cancel()
            try:
                await self._server_task # Wait for the task to acknowledge cancellation
            except asyncio.CancelledError:
                logger.info("Internal API server loop task successfully cancelled.")
            except Exception as e:
                logger.error(f"Error waiting for server loop task cancellation: {e}", exc_info=True)

        # Stop the TCPSite
        if self.site:
            try:
                await self.site.stop()
                logger.info("Internal API server site stopped.")
                self.site = None
            except Exception as e:
                logger.error(f"Error stopping Internal API site: {e}", exc_info=True)

        # Cleanup the AppRunner
        if self.runner:
            try:
                await self.runner.cleanup()
                logger.info("Internal API server runner cleaned up.")
                self.runner = None
            except Exception as e:
                logger.error(f"Error cleaning up Internal API runner: {e}", exc_info=True)
                
        self._server_task = None # Clear the task reference
        logger.info("Internal API server stopped.") 
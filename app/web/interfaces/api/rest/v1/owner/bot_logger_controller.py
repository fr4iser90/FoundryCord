import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

class BotLoggerController(BaseController):
    """Controller for fetching bot logs."""

    def __init__(self):
        super().__init__(prefix="/owner/bot/logger", tags=["Bot Logger"])
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self._register_routes()
        logger.info("BotLoggerController initialized for internal API calls.")

    def _register_routes(self):
        """Register all routes for this controller"""
        self.router.get("/logs")(self.get_bot_logs)
        # Add WebSocket route later if needed
        # self.router.websocket("/ws")(self.websocket_log_stream)

    async def get_bot_logs(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Fetch the latest bot logs via the internal bot API."""
        internal_logs_endpoint = "http://foundrycord-bot:9090/internal/logs"
        
        try:
            # Ensure only owners can access
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can view bot logs."
                )

            # --- Fetch logs from internal API --- 
            try:
                logger.debug(f"Requesting logs from {internal_logs_endpoint}")
                response = await self.http_client.get(internal_logs_endpoint)
                response.raise_for_status()
                
                logs_data = response.json()
                logger.debug(f"Received log data: {logs_data}")
                
                if not isinstance(logs_data, dict) or 'logs' not in logs_data or not isinstance(logs_data['logs'], list):
                     logger.error(f"Invalid log data format received from internal API: {logs_data}")
                     raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Received invalid log format from bot service.")
                     
                return self.success_response(logs_data) 

            except httpx.TimeoutException:
                logger.error(f"Timeout connecting to internal bot API at {internal_logs_endpoint}")
                raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Connection to bot service timed out.")
            except httpx.RequestError as req_err:
                logger.error(f"Error connecting to internal bot API at {internal_logs_endpoint}: {req_err}")
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not connect to bot service to fetch logs.")
            except httpx.HTTPStatusError as status_err:
                 logger.error(f"Internal bot API returned error status {status_err.response.status_code} for logs: {status_err.response.text}")
                 raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Bot service reported an error ({status_err.response.status_code}).")
            # --- End Fetching --- 

        except HTTPException as http_exc:
            # Re-raise HTTPExceptions directly
            raise http_exc
        except Exception as e:
            # Handle unexpected errors
            return self.handle_exception(e)

    async def close_http_client(self):
        """Gracefully close the httpx client."""
        if hasattr(self, 'http_client') and self.http_client:
            await self.http_client.aclose()
            logger.info("HTTP client closed.")

    # TODO: Implement WebSocket endpoint if real-time streaming is desired
    # async def websocket_log_stream(self, websocket: WebSocket, current_user: AppUserEntity = Depends(get_current_user_ws)):
    # ... (rest of websocket code remains the same)

# Controller instance
bot_logger_controller = BotLoggerController()

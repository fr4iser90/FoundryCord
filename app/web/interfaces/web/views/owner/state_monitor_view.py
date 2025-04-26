from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.interfaces.web.views.base_view import BaseView
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

class StateMonitorView(BaseView):
    """View for the State Monitor page."""

    def __init__(self):
        # Define the router with prefix and tags
        super().__init__(APIRouter(prefix="/owner/state-monitor", tags=["Owner State Monitor"]))
        self._register_routes()

    def _register_routes(self):
        """Register routes for this view."""
        # Route for the main state monitor page
        self.router.get("/", response_class=HTMLResponse)(self.state_monitor_page)

    async def state_monitor_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render the state monitor page."""
        try:
            # Ensure only owners can access this page
            await self.require_permission(current_user, "OWNER")

            logger.info(f"User {current_user.username} accessing State Monitor page.")
            
            # Prepare context if needed (e.g., initial data)
            context = {
                # Add any necessary context data here later
            }
            
            # Render the template
            return self.render_template(
                "owner/state-monitor.html", 
                request,
                **context
            )
        except HTTPException as http_exc:
            # Re-raise HTTPExceptions (like 403 Forbidden from require_permission)
            raise http_exc
        except Exception as e:
            logger.error(f"Error loading State Monitor page: {e}", exc_info=True)
            # Return a generic error response
            return self.error_response(request, "An unexpected error occurred while loading the State Monitor page.", 500)

# Create instance for registration
state_monitor_view = StateMonitorView()
# Export the router using the consistent naming convention
router = state_monitor_view.router 
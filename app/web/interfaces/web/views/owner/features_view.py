from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.interfaces.web.views.base_view import BaseView
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

class OwnerFeaturesView(BaseView):
    """View for the Owner Feature Management page."""

    def __init__(self):
        super().__init__(APIRouter(prefix="/owner/features", tags=["Owner Features"]))
        self._register_routes()

    def _register_routes(self):
        """Register routes for this view."""
        self.router.get("/", response_class=HTMLResponse)(self.features_page)

    async def features_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render the owner feature management page."""
        try:
            # Basic Owner Check
            if not current_user.is_owner:
                return self.error_response(request, "Forbidden", 403)

            # TODO: Fetch actual feature configurations later
            context = {
                # Add any necessary context data here later
            }
            
            return self.render_template(
                "owner/features/index.html", 
                request,
                **context
            )
        except Exception as e:
            logger.error(f"Error loading Owner Features page: {e}", exc_info=True)
            return self.error_response(request, "An unexpected error occurred", 500)

# Create instance for registration
owner_features_view = OwnerFeaturesView()
router = owner_features_view.router 
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.interface.logging.api import get_web_logger
from app.web.interfaces.web.views.base_view import BaseView
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

logger = get_web_logger()

class ServerManagementView(BaseView):
    """View for server management functionality"""
    
    def __init__(self):
        super().__init__(APIRouter(prefix="/owner/servers", tags=["Server Management"]))
        services = WebServiceFactory.get_instance().get_services()
        self.server_service = services.get('server_service')
        if not self.server_service:
            logger.error("ServerService could not be initialized for ServerManagementView.")
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this view"""
        self.router.get("", response_class=HTMLResponse)(self.server_management_page)
        self.router.get("/{guild_id}", response_class=HTMLResponse)(self.server_details_page)
    
    async def server_management_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render server management page"""
        try:
            if not current_user or not current_user.is_owner:
                 raise HTTPException(
                     status_code=status.HTTP_403_FORBIDDEN,
                     detail="Only owner can manage servers"
                 )

            logger.info("Fetching manageable servers from ServerService...")
            servers = await self.server_service.get_all_manageable_servers(current_user)
            logger.info(f"Received {len(servers)} servers from ServerService")
            
            server_list = [s.to_dict() for s in servers]

            pending_servers = [s for s in server_list if s.get("access_status", "").lower() == "pending"]
            approved_servers = [s for s in server_list if s.get("access_status", "").lower() == "approved"]
            blocked_servers = [s for s in server_list if s.get("access_status", "").lower() in ["blocked", "rejected", "suspended"]]
            
            logger.info(f"Filtered servers - Pending: {len(pending_servers)}, Approved: {len(approved_servers)}, Blocked/Rejected: {len(blocked_servers)}")
            
            return self.render_template(
                "owner/control/server-list.html",
                request,
                user=current_user,
                active_page="server-management",
                pending_servers=pending_servers,
                approved_servers=approved_servers,
                blocked_servers=blocked_servers
            )
        except HTTPException as e:
            logger.error(f"Access denied to server management: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Error in server management view: {e}", exc_info=True)
            return self.error_response(request, "An unexpected error occurred while loading server management.", 500, user=current_user)
    
    async def server_details_page(self, guild_id: str, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render server details page"""
        try:
            if not current_user or not current_user.is_owner:
                 raise HTTPException(
                     status_code=status.HTTP_403_FORBIDDEN,
                     detail="Only owner can view server details"
                 )
            
            server_entity = await self.server_service.get_server(guild_id)
            
            if not server_entity:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")

            server_details = server_entity.to_dict()

            return self.render_template(
                "owner/control/server-details.html",
                request,
                user=current_user,
                active_page="server-management",
                server=server_details
            )
        except HTTPException as e:
            logger.error(f"HTTP error loading server details for {guild_id}: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Error loading server details for {guild_id}: {e}", exc_info=True)
            return self.error_response(request, f"An unexpected error occurred loading details for server {guild_id}.", 500, user=current_user)

owner_server_management_view = ServerManagementView()
router = owner_server_management_view.router

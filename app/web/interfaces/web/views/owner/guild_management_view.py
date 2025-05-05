from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.interfaces.logging.api import get_web_logger
from app.web.interfaces.web.views.base_view import BaseView
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

logger = get_web_logger()

class GuildManagementView(BaseView):
    """View for guild management functionality"""
    
    def __init__(self):
        super().__init__(APIRouter(prefix="/owner/guilds", tags=["Guild Management"]))
        services = WebServiceFactory.get_instance().get_services()
        self.guild_service = services.get('guild_service')
        if not self.guild_service:
            logger.error("GuildService could not be initialized for GuildManagementView.")
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this view"""
        self.router.get("", response_class=HTMLResponse)(self.guild_management_page)
        # self.router.get("/{guild_id}", response_class=HTMLResponse)(self.guild_details_page)
    
    async def guild_management_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render guild management page"""
        try:
            if not current_user or not current_user.is_owner:
                 raise HTTPException(
                     status_code=status.HTTP_403_FORBIDDEN,
                     detail="Only owner can manage guilds"
                 )

            logger.info("Fetching manageable guilds from GuildService...")
            guilds = await self.guild_service.get_all_manageable_guilds(current_user)
            logger.info(f"Received {len(guilds)} guilds from GuildService")
            
            try:
                guild_list = [g.to_dict() for g in guilds]
            except AttributeError:
                logger.warning("GuildEntity does not have to_dict method, attempting direct attribute access for filtering.")
                guild_list = [
                    {
                        "guild_id": g.guild_id, 
                        "name": g.name,
                        "icon_url": g.icon_url,
                        "member_count": g.member_count,
                        "access_status": g.access_status,
                    }
                    for g in guilds
                ]

            pending_guilds = [g for g in guild_list if g.get("access_status", "").lower() == "pending"]
            approved_guilds = [g for g in guild_list if g.get("access_status", "").lower() == "approved"]
            other_guilds = [g for g in guild_list if g.get("access_status", "").lower() not in ["pending", "approved"]]
            
            logger.info(f"Filtered guilds - Pending: {len(pending_guilds)}, Approved: {len(approved_guilds)}, Other: {len(other_guilds)}")
            
            return self.render_template(
                "owner/control/index.html",
                request,
                user=current_user,
                active_page="guild-management",
                pending_guilds=pending_guilds,
                approved_guilds=approved_guilds,
                other_guilds=other_guilds
            )
        except HTTPException as e:
            logger.error(f"Access denied to guild management: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Error in guild management view: {e}", exc_info=True)
            return self.error_response(request, "An unexpected error occurred while loading guild management.", 500, user=current_user)
    
    # async def guild_details_page(self, guild_id: str, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
    #     """Render guild details page"""
    #     try:
    #         if not current_user or not current_user.is_owner:
    #              raise HTTPException(
    #                  status_code=status.HTTP_403_FORBIDDEN,
    #                  detail="Only owner can view guild details"
    #              )
    #         
    #         guild_entity = None
    #         
    #         if not guild_entity:
    #              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
    #
    #         guild_details = guild_entity.to_dict()
    #
    #         return self.render_template(
    #             "owner/control/server-details.html",
    #             request,
    #             user=current_user,
    #             active_page="guild-management",
    #             guild=guild_details
    #         )
    #     except HTTPException as e:
    #         logger.error(f"HTTP error loading guild details for {guild_id}: {e.detail}")
    #         raise e
    #     except Exception as e:
    #         logger.error(f"Error loading guild details for {guild_id}: {e}", exc_info=True)
    #         return self.error_response(request, f"An unexpected error occurred loading details for guild {guild_id}.", 500, user=current_user)

owner_guild_management_view = GuildManagementView()
router = owner_guild_management_view.router

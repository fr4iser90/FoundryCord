from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.interfaces.web.views.base_view import BaseView
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.repositories.guild_templates import GuildTemplateRepositoryImpl
from app.shared.interfaces.logging.api import get_web_logger
from app.shared.infrastructure.models.discord.entities import GuildConfigEntity
from sqlalchemy import select

logger = get_web_logger() # Assuming get_web_logger is available globally or imported

class GuildDesignerIndexView(BaseView):
    """View for the Guild Designer landing page."""

    def __init__(self):
        # Prefix includes guild_id placeholder
        super().__init__(APIRouter(prefix="/guild/{guild_id}/designer", tags=["Guild Designer"]))
        self._register_routes()

    def _register_routes(self):
        """Register routes for this view."""
        # Route for the designer index page
        self.router.get("/", response_class=HTMLResponse)(self.designer_dashboard)

    async def designer_dashboard(self, request: Request, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Render the guild designer dashboard/index page."""
        try:
            # Permission Check (Example: Requiring Owner or specific permission)
            # TODO: Implement a proper check for 'DESIGNER' or similar guild-specific role/permission
            if not current_user.is_owner:
                 raise HTTPException(status_code=403, detail="Insufficient permissions to access Guild Designer")

            active_template_id = None # Default to None
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                guild_template = await template_repo.get_by_guild_id(guild_id)

                # Fetch Guild Config to get active_template_id
                config_stmt = select(GuildConfigEntity).where(GuildConfigEntity.guild_id == guild_id)
                config_result = await session.execute(config_stmt)
                guild_config = config_result.scalar_one_or_none()
                if guild_config:
                    active_template_id = guild_config.active_template_id
                    logger.debug(f"Found active template ID {active_template_id} for guild {guild_id}")
                else:
                    logger.warning(f"No GuildConfig found for guild {guild_id}. Cannot determine active template.")

                if not guild_template:
                    logger.warning(f"No guild template found for guild {guild_id} for designer view.")
                    # Render a specific template or message indicating no template exists
                    return self.render_template(
                        "guild/designer/no_template.html", # Need to create this template
                        request,
                        guild_id=guild_id,
                        error="No structure template has been saved for this guild yet."
                    )
            
            # If template exists, render the designer dashboard
            return self.render_template(
                "guild/designer/index.html",
                request,
                guild_id=guild_id,
                guild_template_data=guild_template, # Renamed keyword argument
                active_page="guild-designer", # Example active page key
                current_user_id=current_user.id, # Pass the user ID
                active_template_id=active_template_id # Pass the active template ID
            )
        except HTTPException as http_exc:
            # Re-raise HTTP exceptions
            raise http_exc 
        except Exception as e:
            logger.error(f"Error loading Guild Designer dashboard for guild {guild_id}: {e}", exc_info=True)
            return self.error_response(request, "An unexpected error occurred", 500)

# Create instance for registration
guild_designer_index_view = GuildDesignerIndexView()
router = guild_designer_index_view.router

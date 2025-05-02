from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from pydantic import BaseModel # Keep for GuildTemplateSettingsUpdate

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user, get_web_db_session
from app.web.application.services.template.template_service import GuildTemplateService
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, InvalidOperation, ConfigurationNotFound
from app.shared.interface.logging.api import get_web_logger

# TODO: Move this schema to the main schemas file eventually
class GuildTemplateSettingsUpdate(BaseModel):
    delete_unmanaged: bool

logger = get_web_logger()

# TODO: Get this from config/settings more reliably
INTERNAL_API_BASE_URL = "http://foundrycord-bot:9090"

class GuildTemplateLifecycleController(BaseController):
    """Controller for managing guild template activation, application, and settings."""

    def __init__(self):
        # Use the same prefix as other designer controllers
        super().__init__(prefix="/guilds/{guild_id}/template", tags=["Guild Templates (Lifecycle & Settings)"])
        self.template_service = GuildTemplateService()
        self._register_routes()

    def _register_routes(self):
        """Register API routes for template lifecycle actions."""

        # Activate a template for a specific guild
        self.router.post("/templates/{template_id}/activate",
                         status_code=status.HTTP_200_OK,
                         summary="Activate Guild Template for specific Guild",
                         description="Marks a specific template as the active one for the guild.")(self.activate_guild_template)

        # Apply the active template to Discord
        self.router.post("/apply",
                         status_code=status.HTTP_202_ACCEPTED, # Use 202 as it triggers an async task
                         summary="Apply Active Template to Discord",
                         description="Triggers the bot to apply the active template to Discord.")(self.apply_guild_template)

        # Update template application settings for the guild
        self.router.put("/settings",
                        status_code=status.HTTP_200_OK,
                        summary="Update Guild Template Application Settings",
                        description="Updates settings like deleting unmanaged channels.")(self.update_template_settings)


    # --- Method Implementations --- 

    async def activate_guild_template(
        self,
        guild_id: str,
        template_id: int,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to activate a specific guild template for a specific guild."""
        logger.info(f"User {current_user.id} requesting activation for template ID: {template_id} for guild ID: {guild_id}")
        try:
            # Service handles permissions and logic
            await self.template_service.activate_template(
                db=db,
                template_id=template_id,
                target_guild_id=guild_id,
                requesting_user=current_user
            )
            logger.info(f"Template ID {template_id} activated successfully for guild {guild_id} by user {current_user.id}.")
            return {"message": "Template activated successfully."}
        except (TemplateNotFound, PermissionDenied, InvalidOperation) as e:
            status_code = status.HTTP_404_NOT_FOUND
            if isinstance(e, PermissionDenied):
                status_code = status.HTTP_403_FORBIDDEN
            elif isinstance(e, InvalidOperation):
                status_code = status.HTTP_400_BAD_REQUEST
            logger.warning(f"Activation failed for template {template_id} on guild {guild_id}: {e}")
            raise HTTPException(status_code=status_code, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error activating template ID {template_id} for guild {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def apply_guild_template(
        self,
        guild_id: str,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to trigger applying the active template to the Discord guild via Internal API."""
        logger.info(f"User {current_user.id} requesting template application for guild ID: {guild_id}")
        try:
            # Permission check (simple owner check for now)
            if not current_user.is_owner:
                 logger.warning(f"Permission denied: User {current_user.id} attempted to apply template for guild {guild_id}.")
                 raise PermissionDenied("You do not have permission to apply templates to this guild.")

            internal_api_url = f"{INTERNAL_API_BASE_URL}/guilds/{guild_id}/apply_template"
            logger.info(f"Making POST request to internal API: {internal_api_url}")

            # Make request to internal bot API
            async with httpx.AsyncClient() as client:
                 response = await client.post(internal_api_url, timeout=30.0)

            # Handle response from bot
            if response.status_code == 202:
                 logger.info(f"Internal API accepted template application trigger for guild {guild_id}.")
                 response_data = response.json()
                 return {"message": response_data.get("message", "Template application trigger accepted by bot.")}
            else:
                 error_detail = f"Internal bot error (Status: {response.status_code})"
                 try:
                     error_data = response.json()
                     error_detail = error_data.get("message", error_detail)
                 except Exception:
                     error_detail = f"{error_detail}: {response.text[:200]}"
                 logger.error(f"Internal API call failed for guild {guild_id}. Status: {response.status_code}, Detail: {error_detail}")
                 web_status_code = status.HTTP_503_SERVICE_UNAVAILABLE
                 if 400 <= response.status_code < 500:
                     web_status_code = status.HTTP_400_BAD_REQUEST
                 raise HTTPException(status_code=web_status_code, detail=error_detail)

        except httpx.RequestError as exc:
            logger.error(f"HTTP request to internal bot API failed: {exc}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to communicate with the internal bot service.")
        except PermissionDenied as e:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error calling internal API for guild {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def update_template_settings(
        self,
        guild_id: str,
        settings_update: GuildTemplateSettingsUpdate,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to update guild-specific template application settings."""
        logger.info(f"User {current_user.id} updating template settings for guild {guild_id}: {settings_update.model_dump()}")
        try:
            # Permission check
            if not current_user.is_owner:
                 logger.warning(f"Permission denied: User {current_user.id} attempted to update template settings for guild {guild_id}.")
                 raise PermissionDenied("Insufficient permissions to update template settings.")

            # Service handles logic and ConfigurationNotFound exception
            success = await self.template_service.update_template_settings(
                db=db,
                guild_id=guild_id,
                delete_unmanaged=settings_update.delete_unmanaged,
                requesting_user=current_user
            )
            logger.info(f"Successfully updated template settings for guild {guild_id}.")
            return {"message": "Template settings updated successfully."}
        except PermissionDenied as e:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ConfigurationNotFound as e:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating template settings for guild {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

# Instantiate the controller for registration
lifecycle_controller = GuildTemplateLifecycleController()

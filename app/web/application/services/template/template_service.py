"""
Service layer for managing guild structure templates.
Acts as a Facade, delegating calls to more specific template services.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.interface.logging.api import get_web_logger
# Import Schemas (needed for type hints in method signatures)
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import GuildStructureUpdatePayload, GuildStructureTemplateCreateFromStructure
# Import User Entity (needed for type hints)
from app.shared.infrastructure.models.auth import AppUserEntity
# Import Template Entity (needed for type hints)
from app.shared.infrastructure.models.guild_templates import GuildTemplateEntity

# Import the specific services
from .query_service import TemplateQueryService
from .structure_service import TemplateStructureService
from .management_service import TemplateManagementService
from .sharing_service import TemplateSharingService

logger = get_web_logger()

class GuildTemplateService:
    """Facade that delegates template-related logic to specialized services."""

    def __init__(self):
        """Initialize GuildTemplateService and its underlying specific services."""
        self._query_service = TemplateQueryService()
        self._structure_service = TemplateStructureService()
        self._management_service = TemplateManagementService()
        self._sharing_service = TemplateSharingService()
        logger.info("GuildTemplateService Facade initialized, delegating to specific template services.")

    # --- Query Methods Delegation --- 

    async def get_template_by_guild(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Delegates to TemplateQueryService."""
        logger.debug(f"GuildTemplateService facade delegating get_template_by_guild for {guild_id}")
        return await self._query_service.get_template_by_guild(guild_id)

    async def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Delegates to TemplateQueryService."""
        logger.debug(f"GuildTemplateService facade delegating get_template_by_id for {template_id}")
        return await self._query_service.get_template_by_id(template_id)

    async def list_templates(self, user_id: int, context_guild_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Delegates to TemplateQueryService."""
        logger.debug(f"GuildTemplateService facade delegating list_templates for user {user_id}")
        return await self._query_service.list_templates(user_id, context_guild_id)

    async def get_parent_template_id_for_element(self, db: AsyncSession, element_id: int, element_type: str) -> Optional[int]:
        """Delegates to TemplateQueryService."""
        logger.debug(f"GuildTemplateService facade delegating get_parent_template_id_for_element for {element_type} {element_id}")
        # Pass the db session along as the specific service expects it
        return await self._query_service.get_parent_template_id_for_element(db, element_id, element_type)

    # --- Structure Methods Delegation --- 

    async def update_template_structure(
        self, db: AsyncSession, template_id: int, structure_payload: GuildStructureUpdatePayload, requesting_user: AppUserEntity
    ) -> Dict[str, Any]:
        """Delegates to TemplateStructureService."""
        logger.debug(f"GuildTemplateService facade delegating update_template_structure for {template_id}")
        return await self._structure_service.update_template_structure(db, template_id, structure_payload, requesting_user)

    async def create_template_from_structure(
        self, db: AsyncSession, creator_user_id: int, payload: GuildStructureTemplateCreateFromStructure
    ) -> GuildTemplateEntity:
        """Delegates to TemplateStructureService."""
        logger.debug(f"GuildTemplateService facade delegating create_template_from_structure for user {creator_user_id}")
        return await self._structure_service.create_template_from_structure(db, creator_user_id, payload)

    # --- Management Methods Delegation --- 

    async def delete_template(self, template_id: int) -> bool:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating delete_template for {template_id}")
        return await self._management_service.delete_template(template_id)

    async def activate_template(self, db: AsyncSession, template_id: int, target_guild_id: str, requesting_user: AppUserEntity) -> None:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating activate_template for {template_id}, guild {target_guild_id}")
        await self._management_service.activate_template(db, template_id, target_guild_id, requesting_user)

    async def check_user_can_edit_template(self, db: AsyncSession, user_id: int, template_id: int) -> bool:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating check_user_can_edit_template for user {user_id}, template {template_id}")
        return await self._management_service.check_user_can_edit_template(db, user_id, template_id)

    async def update_template_settings(self, db: AsyncSession, guild_id: str, delete_unmanaged: bool, requesting_user: AppUserEntity) -> bool:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating update_template_settings for guild {guild_id}")
        return await self._management_service.update_template_settings(db, guild_id, delete_unmanaged, requesting_user)

    async def delete_template_category(self, db: AsyncSession, category_id: int) -> bool:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating delete_template_category for {category_id}")
        return await self._management_service.delete_template_category(db, category_id)

    async def delete_template_channel(self, db: AsyncSession, channel_id: int) -> bool:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating delete_template_channel for {channel_id}")
        return await self._management_service.delete_template_channel(db, channel_id)

    async def update_template_metadata(
        self, db: AsyncSession, template_id: int, requesting_user: AppUserEntity, 
        new_name: Optional[str] = None, new_description: Optional[str] = None, is_shared: Optional[bool] = None
    ) -> GuildTemplateEntity:
        """Delegates to TemplateManagementService."""
        logger.debug(f"GuildTemplateService facade delegating update_template_metadata for {template_id}")
        # Pass arguments in the correct order expected by the management service
        return await self._management_service.update_template_metadata(
            db, template_id, requesting_user, new_name, new_description, is_shared
        )

    # --- Sharing Methods Delegation --- 

    async def list_shared_templates(self) -> List[Dict[str, Any]]:
        """Delegates to TemplateSharingService."""
        logger.debug(f"GuildTemplateService facade delegating list_shared_templates")
        return await self._sharing_service.list_shared_templates()

    async def get_shared_template_details(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Delegates to TemplateSharingService."""
        logger.debug(f"GuildTemplateService facade delegating get_shared_template_details for {template_id}")
        return await self._sharing_service.get_shared_template_details(template_id)

    async def copy_shared_template(self, shared_template_id: int, user_id: int, new_name_optional: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Delegates to TemplateSharingService."""
        logger.debug(f"GuildTemplateService facade delegating copy_shared_template for {shared_template_id}, user {user_id}")
        return await self._sharing_service.copy_shared_template(shared_template_id, user_id, new_name_optional)

    async def share_template(self, original_template_id: int, new_name: str, new_description: Optional[str], creator_user_id: int) -> Optional[Dict[str, Any]]:
        """Delegates to TemplateSharingService. (Note: Current impl copies privately)."""
        logger.debug(f"GuildTemplateService facade delegating share_template (copy) for {original_template_id}, user {creator_user_id}")
        return await self._sharing_service.share_template(original_template_id, new_name, new_description, creator_user_id)

# Instantiate the service if needed globally (e.g., for factory)
# Or instantiate it where needed
# guild_template_service = GuildTemplateService() 

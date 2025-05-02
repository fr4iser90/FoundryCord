"""
SQLAlchemy implementation for the Dashboard Component Definition Repository.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.repositories.dashboards.dashboard_component_definition_repository import DashboardComponentDefinitionRepository
from app.shared.infrastructure.models.dashboards import DashboardComponentDefinitionEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class DashboardComponentDefinitionRepositoryImpl(
    BaseRepositoryImpl[DashboardComponentDefinitionEntity],
    DashboardComponentDefinitionRepository
):
    """SQLAlchemy implementation for accessing dashboard component definitions."""

    def __init__(self, session: AsyncSession):
        """Initializes the repository with an async session."""
        super().__init__(DashboardComponentDefinitionEntity, session)
        logger.debug("DashboardComponentDefinitionRepositoryImpl initialized.")

    async def list_definitions(
        self,
        dashboard_type: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[DashboardComponentDefinitionEntity]:
        """Retrieves a list of component definitions, optionally filtered."""
        logger.debug(f"Repository: Listing definitions (dashboard_type={dashboard_type}, component_type={component_type})")
        
        stmt = select(self.model)
        
        if dashboard_type:
            stmt = stmt.where(self.model.dashboard_type == dashboard_type)
        
        if component_type:
            stmt = stmt.where(self.model.component_type == component_type)
            
        # Add ordering for consistency, e.g., by dashboard_type then component_key
        stmt = stmt.order_by(self.model.dashboard_type, self.model.component_key)
            
        result = await self.session.execute(stmt)
        definitions = list(result.scalars().all()) # Use list() to ensure List type
        
        logger.debug(f"Repository: Found {len(definitions)} component definitions.")
        return definitions 
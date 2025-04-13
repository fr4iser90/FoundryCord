from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_web_db_session # Reuse session dependency
from app.shared.domain.repositories.ui.ui_layout_repository import UILayoutRepository
from app.shared.infrastructure.repositories.ui.ui_layout_repository_impl import UILayoutRepositoryImpl
from app.web.application.services.ui.layout_service import LayoutService

# Dependency to get UILayoutRepository instance
def get_layout_repository(session: AsyncSession = Depends(get_web_db_session)) -> UILayoutRepository:
    """Provides an instance of UILayoutRepositoryImpl with a session."""
    return UILayoutRepositoryImpl(session)

# Dependency to get LayoutService instance
async def get_layout_service(
    session: Annotated[AsyncSession, Depends(get_web_db_session)]
) -> LayoutService:
    """Dependency provider for LayoutService."""
    repository = UILayoutRepositoryImpl(session=session)
    service = LayoutService(layout_repository=repository)
    return service 
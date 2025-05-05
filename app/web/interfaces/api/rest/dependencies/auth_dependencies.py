"""FastAPI dependencies for authentication and authorization"""
from fastapi import Depends, Request, HTTPException, status
# Import the session factory
from app.shared.infrastructure.database.session.factory import get_session
# Import repository interface and implementation
from app.shared.domain.repositories.auth import UserRepository
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interfaces.logging.api import get_web_logger
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator # Import AsyncGenerator for session dependency
from app.web.infrastructure.startup.lifecycle_manager import WebLifecycleManager

logger = get_web_logger()

# Dependency to provide a database session per request using the factory
async def get_web_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an AsyncSession using the get_session factory."""
    session_generator = get_session()
    async for session in session_generator:
        try:
            yield session
        finally:
            # The factory's context manager should handle commit/rollback/close
            pass 

# Dependency to get UserRepository instance using the correct session dependency
async def get_user_repository(session: AsyncSession = Depends(get_web_db_session)) -> UserRepository:
    """Dependency to provide UserRepository instance."""
    return UserRepositoryImpl(session)

async def get_current_user(request: Request, user_repo: UserRepository = Depends(get_user_repository)) -> AppUserEntity:
    """Get the authenticated user from session, loading full details from DB."""
    user_data_from_session = request.session.get("user")
    if not user_data_from_session or 'id' not in user_data_from_session:
        logger.warning("Authentication required: No user data or user ID in session.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_id = user_data_from_session['id']
    
    try:
        user = await user_repo.get_by_id(user_id) 
        if not user:
            logger.error(f"Authenticated user ID {user_id} not found in database!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found"
            )
        
        if not hasattr(user, 'permissions') or not user.permissions:
             logger.warning(f"User {user_id} loaded, but permissions attribute is missing or empty after repository call.")
             raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail="Failed to load user permissions."
             )

        logger.debug(f"get_current_user returning user {user.id} with permissions: {user.permissions}")
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Error retrieving user {user_id} from database: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user data"
        )

async def get_lifecycle_manager(request: Request) -> WebLifecycleManager:
    """Dependency to get the WebLifecycleManager instance from app state."""
    manager = getattr(request.app.state, 'lifecycle_manager', None)
    if not manager:
        logger.error("WebLifecycleManager not found in app state!")
        raise HTTPException(status_code=500, detail="Internal server error: Lifecycle manager unavailable")
    return manager

async def get_key_service(manager: WebLifecycleManager = Depends(get_lifecycle_manager)) -> KeyManagementService:
    """Get the managed key management service instance."""
    key_service = manager.get_component('key_service')
    if not key_service:
        logger.error("KeyManagementService not found in lifecycle manager components!")
        raise HTTPException(status_code=500, detail="Internal server error: Key service unavailable")
    if not key_service.initialized:
         logger.warning("KeyManagementService accessed via dependency before initialization completed!")
         # Optionally wait or raise, depending on desired behavior
         # await asyncio.sleep(0.1) # Simple wait, might not be robust
         # raise HTTPException(status_code=503, detail="Service not ready") 
    return key_service

async def get_auth_service(manager: WebLifecycleManager = Depends(get_lifecycle_manager)) -> AuthenticationService:
    """Get the managed authentication service instance."""
    auth_service = manager.get_component('auth_service')
    if not auth_service:
        logger.error("AuthenticationService not found in lifecycle manager components!")
        raise HTTPException(status_code=500, detail="Internal server error: Auth service unavailable")
    if not hasattr(auth_service, 'key_service') or not auth_service.key_service.initialized:
        logger.warning("AuthenticationService or its KeyService accessed via dependency before initialization completed!")
    return auth_service

async def get_authz_service(manager: WebLifecycleManager = Depends(get_lifecycle_manager)) -> AuthorizationService:
    """Get the managed authorization service instance."""
    authz_service = manager.get_component('authz_service')
    if not authz_service:
        logger.error("AuthorizationService not found in lifecycle manager components!")
        raise HTTPException(status_code=500, detail="Internal server error: Authz service unavailable")
    # Add similar initialization checks if needed
    return authz_service 
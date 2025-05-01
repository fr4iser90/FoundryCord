from typing import Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.interface.logging.api import get_db_logger

# Define a type variable for the SQLAlchemy model entity
EntityType = TypeVar('EntityType')

# Initialize logger
logger = get_db_logger()

class BaseRepositoryImpl(Generic[EntityType]):
    """Base class for SQLAlchemy repository implementations."""

    def __init__(self, model_cls: Type[EntityType], session: AsyncSession):
        """Initialize the base repository.

        Args:
            model_cls: The SQLAlchemy model class this repository handles.
            session: The SQLAlchemy AsyncSession to use for database operations.
        """
        self.model = model_cls
        self.session = session

    async def delete(self, entity_instance: EntityType) -> None:
        """Deletes a given entity instance from the session."""
        if not isinstance(entity_instance, self.model):
            msg = f"Attempted to delete an object of type {type(entity_instance).__name__} from a repository for {self.model.__name__}"
            logger.error(msg)
            raise TypeError(msg)

        try:
            await self.session.delete(entity_instance)
            # Flush to ensure the delete operation is processed within the transaction
            # Caller is responsible for commit/rollback
            await self.session.flush()
            logger.debug(f"Marked entity {entity_instance} for deletion (pending commit).")
        except Exception as e:
            # Log error but let the caller handle transaction rollback
            logger.error(f"Error marking entity {entity_instance} for deletion: {e}", exc_info=True)
            raise # Re-raise the exception for the service layer to handle

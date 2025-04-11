from typing import Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

# Define a type variable for the SQLAlchemy model entity
EntityType = TypeVar('EntityType')

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

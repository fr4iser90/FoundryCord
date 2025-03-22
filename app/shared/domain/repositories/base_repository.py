from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar('T')
ID = TypeVar('ID')

class BaseRepository(Generic[T, ID], ABC):
    """Base repository interface for all repositories"""
    
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Get all entities"""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity: T) -> None:
        """Delete an entity"""
        pass
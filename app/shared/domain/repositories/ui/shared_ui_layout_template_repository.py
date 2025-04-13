from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# Import the entity this repository works with
from app.shared.infrastructure.models.ui import SharedUILayoutTemplateEntity

class SharedUILayoutTemplateRepository(ABC):
    """
    Interface for data access operations related to shared UI layout templates.
    """

    @abstractmethod
    async def create(
        self, 
        name: str, 
        layout_data: Dict[str, Any], 
        creator_user_id: Optional[int] = None, 
        description: Optional[str] = None
    ) -> Optional[SharedUILayoutTemplateEntity]:
        """
        Creates a new shared layout template.

        Args:
            name: The unique name for the shared template.
            layout_data: The JSON-serializable layout data (grid items, lock status, etc.).
            creator_user_id: Optional ID of the user creating the template.
            description: Optional description for the template.

        Returns:
            The created SharedUILayoutTemplateEntity if successful, otherwise None.
        """
        pass

    @abstractmethod
    async def get_by_id(self, template_id: int) -> Optional[SharedUILayoutTemplateEntity]:
        """
        Retrieves a shared template by its unique ID.

        Args:
            template_id: The ID of the template.

        Returns:
            The SharedUILayoutTemplateEntity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[SharedUILayoutTemplateEntity]:
        """
        Retrieves a shared template by its unique name.

        Args:
            name: The name of the template.

        Returns:
            The SharedUILayoutTemplateEntity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[SharedUILayoutTemplateEntity]:
        """
        Retrieves all shared layout templates.

        Returns:
            A list of all SharedUILayoutTemplateEntity objects.
        """
        pass

    @abstractmethod
    async def update(
        self, 
        template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        layout_data: Optional[Dict[str, Any]] = None
    ) -> Optional[SharedUILayoutTemplateEntity]:
        """
        Updates an existing shared layout template.

        Args:
            template_id: The ID of the template to update.
            name: The new name (if changing).
            description: The new description (if changing).
            layout_data: The new layout data (if changing).

        Returns:
            The updated SharedUILayoutTemplateEntity if successful, otherwise None.
        """
        pass

    @abstractmethod
    async def delete(self, template_id: int) -> bool:
        """
        Deletes a shared layout template by its ID.

        Args:
            template_id: The ID of the template to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        pass

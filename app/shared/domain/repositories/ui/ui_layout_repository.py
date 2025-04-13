from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# Assuming the entity path is correct
from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity

class UILayoutRepository(ABC):
    """
    Interface for data access operations related to UI layouts.
    """

    @abstractmethod
    async def get_layout(self, user_id: int, page_identifier: str) -> Optional[UILayoutEntity]:
        """
        Retrieves the layout for a specific user and page identifier.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page/context.

        Returns:
            The UILayoutEntity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def save_layout(self, user_id: int, page_identifier: str, layout_data: Dict[str, Any]) -> UILayoutEntity:
        """
        Saves or updates the layout for a specific user and page identifier.
        If a layout exists, it updates the layout_data and updated_at timestamp.
        If no layout exists, it creates a new entry.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page/context.
            layout_data: The JSON-serializable layout data (e.g., from Gridstack).

        Returns:
            The saved or updated UILayoutEntity.
        """
        pass

    @abstractmethod
    async def delete_layout(self, user_id: int, page_identifier: str) -> bool:
        """
        Deletes the layout for a specific user and page identifier.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page/context.

        Returns:
            True if deletion was successful or entry didn't exist, False on error.
        """
        pass

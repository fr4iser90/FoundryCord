from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

# Assuming the entity path is correct
from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity

class UILayoutRepository(ABC):
    """
    Interface for data access operations related to UI layouts.
    """

    @abstractmethod
    async def get_layout(self, user_id: int, page_identifier: str) -> Optional[UILayoutEntity]:
        """
        Retrieves the layout entity for a specific user and page identifier.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page/context.

        Returns:
            The UILayoutEntity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def list_layouts(self, user_id: int, guild_id: Optional[str] = None, scope: Optional[str] = None) -> List[UILayoutEntity]:
        """
        Retrieves a list of layout entities based on filter criteria.
        (Implementation needs to handle filtering logic based on page_identifier format, 
         or potential future columns like 'scope' or 'guild_id' on the entity).

        Args:
            user_id: The ID of the user requesting the list.
            guild_id: Optional guild ID to filter by (if applicable).
            scope: Optional scope ('guild', 'shared', 'user') to filter by (if applicable).

        Returns:
            A list of UILayoutEntity objects matching the criteria.
        """
        pass

    @abstractmethod
    async def save_layout(self, user_id: int, page_identifier: str, layout_data: Dict[str, Any]) -> UILayoutEntity:
        """
        Saves or updates the layout for a specific user and page identifier.
        The layout_data dictionary should contain the grid structure AND the is_locked status.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page/context.
            layout_data: The JSON-serializable layout data including grid items and lock status.

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

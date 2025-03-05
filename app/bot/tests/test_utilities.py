import pytest
from unittest.mock import patch

# Import your utility modules
from core.services.logging.logging_commands import logger

class TestLogger:
    def test_logger_initialization(self):
        """Test that the logger is properly initialized"""
        assert logger is not None
        assert logger.name == "homelab_bot"

class TestPermissions:
    @patch("core.utilities.permissions.get_user_role")
    def test_is_admin(self, mock_get_user_role):
        """Test the is_admin function"""
        from core.utilities.permissions import is_admin
        
        # Test admin case
        mock_get_user_role.return_value = "admin"
        assert is_admin("123456789") is True
        
        # Test non-admin case
        mock_get_user_role.return_value = "user"
        assert is_admin("123456789") is False
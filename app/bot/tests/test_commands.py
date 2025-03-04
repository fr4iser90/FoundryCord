import pytest
from unittest.mock import AsyncMock, patch

# Import your command modules
# from core.commands.admin_commands import ...

# Mark all tests as async
pytestmark = pytest.mark.asyncio

class TestAdminCommands:
    @patch("core.commands.admin_commands.is_admin")
    async def test_admin_command(self, mock_is_admin, mock_discord_ctx):
        """Test an admin command"""
        # Mock the admin check to return True
        mock_is_admin.return_value = True
        
        # Import the command function
        from core.commands.admin_commands import some_admin_command
        
        # Call the command
        await some_admin_command(mock_discord_ctx, "test_arg")
        
        # Assert the command responded correctly
        mock_discord_ctx.send.assert_called_once()
        assert "success" in mock_discord_ctx.send.call_args[0][0].lower()

class TestUserCommands:
    async def test_user_command(self, mock_discord_ctx):
        """Test a user command"""
        # Import the command function
        from core.commands.user_commands import some_user_command
        
        # Call the command
        await some_user_command(mock_discord_ctx)
        
        # Assert the command responded correctly
        mock_discord_ctx.send.assert_called_once()
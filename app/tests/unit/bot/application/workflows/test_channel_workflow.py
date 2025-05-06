import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import nextcord

from app.bot.application.workflows.channel_workflow import ChannelWorkflow, WorkflowStatus
from app.bot.application.workflows.database_workflow import DatabaseWorkflow
from app.bot.application.workflows.category_workflow import CategoryWorkflow
from app.shared.infrastructure.repositories.discord import GuildConfigRepositoryImpl

# --- Fixtures ---

@pytest.fixture
def mock_db_workflow():
    return MagicMock(spec=DatabaseWorkflow)

@pytest.fixture
def mock_category_workflow():
    return MagicMock(spec=CategoryWorkflow)

@pytest.fixture
def mock_bot():
    bot = AsyncMock(name="MockBot")
    bot.get_guild = MagicMock(return_value=MagicMock(spec=nextcord.Guild))
    return bot

@pytest.fixture
def channel_workflow(mock_db_workflow, mock_category_workflow, mock_bot):
    return ChannelWorkflow(database_workflow=mock_db_workflow, category_workflow=mock_category_workflow, bot=mock_bot)

@pytest.fixture
def mock_guild_config_repo_instance():
    repo = AsyncMock(spec=GuildConfigRepositoryImpl)
    repo.get_by_guild_id = AsyncMock(return_value=MagicMock(name="MockGuildConfig")) # Default to config found
    return repo

@pytest.fixture
def mock_guild_config_repository_impl_class(mocker, mock_guild_config_repo_instance):
    return mocker.patch(
        "app.bot.application.workflows.channel_workflow.GuildConfigRepositoryImpl",
        return_value=mock_guild_config_repo_instance
    )

@pytest.fixture
def mock_session_context(mocker):
    mock_session = AsyncMock(name="MockDbSession")
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_session
    async_context_manager.__aexit__.return_value = None
    return mocker.patch(
        "app.bot.application.workflows.channel_workflow.session_context", 
        return_value=async_context_manager
    )

# --- Tests ---

@pytest.mark.asyncio
async def test_initialize_success(channel_workflow):
    """Test global initialization success."""
    result = await channel_workflow.initialize()
    assert result is True

@pytest.mark.asyncio
async def test_initialize_for_guild_success(channel_workflow, mock_bot, mock_session_context, mock_guild_config_repository_impl_class, mock_guild_config_repo_instance):
    """Test successful initialization for a guild."""
    guild_id = "123"
    # Configure the mock guild returned by bot.get_guild to have the correct ID
    mock_guild_instance = MagicMock(spec=nextcord.Guild)
    mock_guild_instance.id = int(guild_id)
    mock_bot.get_guild.return_value = mock_guild_instance
    
    result = await channel_workflow.initialize_for_guild(guild_id)
    
    assert result is True
    assert channel_workflow.guild_status[guild_id] == WorkflowStatus.ACTIVE
    mock_bot.get_guild.assert_called_once_with(int(guild_id))
    mock_session_context.assert_called_once()
    mock_guild_config_repository_impl_class.assert_called_once_with(mock_session_context.return_value.__aenter__.return_value)
    mock_guild_config_repo_instance.get_by_guild_id.assert_awaited_once_with(str(int(guild_id))) # Ensure it's string ID

@pytest.mark.asyncio
async def test_initialize_for_guild_no_config_found(channel_workflow, mock_bot, mock_session_context, mock_guild_config_repository_impl_class, mock_guild_config_repo_instance, mocker):
    """Test init_for_guild when no guild config is found (should still succeed and log warning)."""
    mock_logger_warning = mocker.patch("app.bot.application.workflows.channel_workflow.logger.warning")
    mock_guild_config_repo_instance.get_by_guild_id.return_value = None # Simulate config not found
    guild_id = "456"
    
    # Configure the mock guild returned by bot.get_guild to have the correct ID for this test case too
    mock_guild_instance = MagicMock(spec=nextcord.Guild)
    mock_guild_instance.id = int(guild_id)
    mock_bot.get_guild.return_value = mock_guild_instance

    result = await channel_workflow.initialize_for_guild(guild_id)
    
    assert result is True # Still active, as per code logic
    assert channel_workflow.guild_status[guild_id] == WorkflowStatus.ACTIVE
    
    # Check that the specific warning about no config was logged
    expected_warning_no_config = f"No GuildConfig found for guild {guild_id}, cannot determine channel settings (assuming enabled)."
    # Check that the second, general warning about template-driven structure was also logged
    expected_warning_template_info = f"ChannelWorkflow.initialize_for_guild: Guild {guild_id} channel structure comes from applied template. Workflow only manages state."
    
    # Assert that warning was called at least for the no_config case
    # We expect two calls in total
    assert mock_logger_warning.call_count == 2
    
    # Check if the expected_warning_no_config is among the calls
    call_args_list = [call[0][0] for call in mock_logger_warning.call_args_list]
    assert expected_warning_no_config in call_args_list
    assert expected_warning_template_info in call_args_list

@pytest.mark.asyncio
async def test_initialize_for_guild_db_error_on_config_fetch(channel_workflow, mock_bot, mock_session_context, mock_guild_config_repository_impl_class, mock_guild_config_repo_instance, mocker):
    """Test init_for_guild when fetching guild config fails."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.channel_workflow.logger.error")
    mock_guild_config_repo_instance.get_by_guild_id.side_effect = Exception("DB Error!")
    guild_id = "789"

    # Configure the mock guild returned by bot.get_guild for this test case
    mock_guild_instance = MagicMock(spec=nextcord.Guild)
    mock_guild_instance.id = int(guild_id) # Though not strictly used by repo call here, good for consistency
    mock_bot.get_guild.return_value = mock_guild_instance

    result = await channel_workflow.initialize_for_guild(guild_id)
    
    assert result is False
    assert channel_workflow.guild_status[guild_id] == WorkflowStatus.FAILED
    mock_logger_error.assert_called_once()
    assert f"Failed to get session or check guild config in ChannelWorkflow for guild {guild_id}" in mock_logger_error.call_args[0][0]

@pytest.mark.asyncio
async def test_cleanup(channel_workflow, mocker):
    """Test cleanup calls super().cleanup."""
    mock_super_cleanup = mocker.patch("app.bot.application.workflows.base_workflow.BaseWorkflow.cleanup", new_callable=AsyncMock)
    await channel_workflow.cleanup()
    mock_super_cleanup.assert_awaited_once()

@pytest.mark.asyncio
async def test_cleanup_guild(channel_workflow, mocker):
    """Test cleanup_guild calls super().cleanup_guild."""
    mock_super_cleanup_guild = mocker.patch("app.bot.application.workflows.base_workflow.BaseWorkflow.cleanup_guild", new_callable=AsyncMock)
    guild_id = "111"
    await channel_workflow.cleanup_guild(guild_id)
    mock_super_cleanup_guild.assert_awaited_once() 
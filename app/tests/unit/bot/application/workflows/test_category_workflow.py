import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.bot.application.workflows.category_workflow import CategoryWorkflow, WorkflowStatus
from app.bot.application.workflows.database_workflow import DatabaseWorkflow
import nextcord

# --- Fixtures ---

@pytest.fixture
def mock_db_workflow():
    return MagicMock(spec=DatabaseWorkflow)

@pytest.fixture
def mock_bot():
    bot = AsyncMock(name="MockBot")
    bot.get_guild = MagicMock(return_value=MagicMock(spec=nextcord.Guild))
    return bot

@pytest.fixture
def category_workflow(mock_db_workflow, mock_bot):
    return CategoryWorkflow(database_workflow=mock_db_workflow, bot=mock_bot)

# --- Tests ---

@pytest.mark.asyncio
async def test_initialize_success(category_workflow):
    """Test global initialization success."""
    result = await category_workflow.initialize()
    assert result is True

@pytest.mark.asyncio
async def test_initialize_for_guild_success(category_workflow, mock_bot):
    """Test successful initialization for a guild."""
    guild_id = "123"
    result = await category_workflow.initialize_for_guild(guild_id)
    
    assert result is True
    assert category_workflow.guild_status[guild_id] == WorkflowStatus.ACTIVE
    mock_bot.get_guild.assert_called_once_with(int(guild_id))

@pytest.mark.asyncio
async def test_initialize_for_guild_no_bot(mocker):
    """Test initialization failure when bot is missing."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.category_workflow.logger.error")
    workflow = CategoryWorkflow(database_workflow=MagicMock(), bot=None) 
    guild_id = "456"
    
    result = await workflow.initialize_for_guild(guild_id)
    
    assert result is False
    assert workflow.guild_status[guild_id] == WorkflowStatus.FAILED
    mock_logger_error.assert_called_once_with("Bot instance not available")

@pytest.mark.asyncio
async def test_initialize_for_guild_not_found(category_workflow, mock_bot, mocker):
    """Test initialization failure when guild is not found."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.category_workflow.logger.error")
    mock_bot.get_guild.return_value = None
    guild_id = "789"
    
    result = await category_workflow.initialize_for_guild(guild_id)
    
    assert result is False
    mock_bot.get_guild.assert_called_once_with(int(guild_id))
    assert category_workflow.guild_status[guild_id] == WorkflowStatus.FAILED
    mock_logger_error.assert_called_once_with(f"Could not find guild {guild_id}")

@pytest.mark.asyncio
async def test_cleanup(category_workflow, mocker):
    """Test cleanup calls super().cleanup."""
    mock_super_cleanup = mocker.patch("app.bot.application.workflows.base_workflow.BaseWorkflow.cleanup", new_callable=AsyncMock)
    await category_workflow.cleanup()
    mock_super_cleanup.assert_awaited_once()

@pytest.mark.asyncio
async def test_cleanup_guild(category_workflow, mocker):
    """Test cleanup_guild calls super().cleanup_guild."""
    mock_super_cleanup_guild = mocker.patch("app.bot.application.workflows.base_workflow.BaseWorkflow.cleanup_guild", new_callable=AsyncMock)
    guild_id = "111"
    await category_workflow.cleanup_guild(guild_id)
    mock_super_cleanup_guild.assert_awaited_once() 
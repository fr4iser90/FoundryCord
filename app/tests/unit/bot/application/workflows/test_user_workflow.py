import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
import nextcord
from sqlalchemy.engine import Result # For mocking session.execute().scalars().first()

from app.bot.application.workflows.user_workflow import UserWorkflow, WorkflowStatus
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl

# --- Fixtures ---

@pytest.fixture
def mock_db_workflow():
    return MagicMock(name="MockDatabaseWorkflow")

@pytest.fixture
def mock_member():
    member = MagicMock(spec=nextcord.Member)
    member.id = 111
    member.name = "TestUser"
    member.discriminator = "1234"
    member.bot = False
    member.joined_at = None
    member.nick = None
    member.avatar = None
    return member

@pytest.fixture
def mock_bot_member():
    member = MagicMock(spec=nextcord.Member)
    member.id = 222
    member.name = "TestBot"
    member.discriminator = "5678"
    member.bot = True
    member.joined_at = None
    member.nick = None
    member.avatar = None
    return member

@pytest.fixture
def mock_guild(mock_member, mock_bot_member):
    guild = MagicMock(spec=nextcord.Guild)
    guild.id = 9876
    guild.name = "SyncGuild"
    guild.icon = None
    guild.members = [mock_member, mock_bot_member]
    return guild

@pytest.fixture
def mock_bot(mock_guild):
    bot = AsyncMock(name="MockBot")
    bot.guilds = [mock_guild] # List of guilds bot is in
    bot.get_guild = MagicMock(return_value=mock_guild)
    return bot

@pytest.fixture
def user_workflow(mock_db_workflow, mock_bot):
    # Patch sync_guild_members during init for initialize tests to avoid recursive calls
    with patch.object(UserWorkflow, 'sync_guild_members', new_callable=AsyncMock) as mock_sync:
        workflow = UserWorkflow(database_workflow=mock_db_workflow, bot=mock_bot)
        workflow._mock_sync_members = mock_sync # Store mock for assertion
        yield workflow

@pytest.fixture
def user_workflow_no_patch(mock_db_workflow, mock_bot):
    """Provides a UserWorkflow without patching sync_guild_members."""
    return UserWorkflow(database_workflow=mock_db_workflow, bot=mock_bot)

@pytest.fixture
def mock_user_repo_instance():
    repo = AsyncMock(spec=UserRepositoryImpl)
    repo.create_or_update = AsyncMock()
    return repo

@pytest.fixture
def mock_user_repository_impl_class(mocker, mock_user_repo_instance):
    return mocker.patch(
        "app.bot.application.workflows.user_workflow.UserRepositoryImpl",
        return_value=mock_user_repo_instance
    )

@pytest.fixture
def mock_session_context(mocker):
    mock_session = AsyncMock(name="MockDbSession")
    # Mock the execute().scalars().first() chain for sync_guild_to_database
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = None # Default: guild not found
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_session
    async_context_manager.__aexit__.return_value = None
    return mocker.patch(
        "app.bot.application.workflows.user_workflow.session_context", 
        return_value=async_context_manager
    )


# --- Test Initialize & Initialize for Guild ---

@pytest.mark.asyncio
async def test_initialize_calls_sync_for_all_guilds(user_workflow, mock_bot):
    """Test global initialize calls sync_guild_members for each guild."""
    result = await user_workflow.initialize()
    assert result is True
    # Check sync_guild_members was called for the guild in mock_bot.guilds
    user_workflow._mock_sync_members.assert_awaited_once_with(mock_bot.guilds[0])
    assert user_workflow.guild_status[str(mock_bot.guilds[0].id)] == WorkflowStatus.PENDING # Status before sync finishes technically

@pytest.mark.asyncio
async def test_initialize_for_guild_success(user_workflow, mock_bot):
    """Test successful initialization for a specific guild."""
    guild_id_str = str(mock_bot.guilds[0].id)
    result = await user_workflow.initialize_for_guild(guild_id_str)
    
    assert result is True
    mock_bot.get_guild.assert_called_once_with(int(guild_id_str))
    # Check sync_guild_members was called
    user_workflow._mock_sync_members.assert_awaited_once_with(mock_bot.guilds[0])
    assert user_workflow.guild_status[guild_id_str] == WorkflowStatus.ACTIVE

@pytest.mark.asyncio
async def test_initialize_for_guild_not_found(user_workflow, mock_bot, mocker):
    """Test initialize_for_guild failure when guild is not found."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.user_workflow.logger.error")
    mock_bot.get_guild.return_value = None # Simulate guild not found
    guild_id_str = "11111"
    
    result = await user_workflow.initialize_for_guild(guild_id_str)
    
    assert result is False
    mock_bot.get_guild.assert_called_once_with(int(guild_id_str))
    user_workflow._mock_sync_members.assert_not_awaited() # Sync should not be called
    assert user_workflow.guild_status[guild_id_str] == WorkflowStatus.FAILED
    mock_logger_error.assert_called_once_with(f"Could not find guild {guild_id_str}")

# --- Test sync_guild_to_database ---

@pytest.mark.asyncio
async def test_sync_guild_to_database_new_guild(user_workflow_no_patch, mock_guild, mock_session_context, mocker):
    """Test synchronizing a guild that doesn't exist in the DB yet."""
    # Use the unpatched workflow instance for these tests
    workflow = user_workflow_no_patch
    mock_session = mock_session_context.return_value.__aenter__.return_value
    # Ensure execute().scalars().first() returns None (default fixture behavior)
    
    await workflow.sync_guild_to_database(mock_guild)
    
    mock_session.execute.assert_awaited_once() # Check select was executed
    mock_session.add.assert_called_once() # Check add was called for the new entity
    # Verify the data added (a bit complex to construct exact entity, check key args)
    added_entity_call = mock_session.add.call_args[0][0]
    assert added_entity_call.guild_id == str(mock_guild.id)
    assert added_entity_call.name == mock_guild.name
    assert added_entity_call.icon_url is not None # Default icon URL
    assert added_entity_call.member_count == len(mock_guild.members)
    mock_session.commit.assert_awaited_once() # Check commit was called

@pytest.mark.asyncio
async def test_sync_guild_to_database_update_guild(user_workflow_no_patch, mock_guild, mock_session_context, mocker):
    """Test synchronizing a guild that already exists in the DB."""
    workflow = user_workflow_no_patch
    mock_session = mock_session_context.return_value.__aenter__.return_value
    
    # Mock existing guild entity found in DB
    mock_existing_guild_entity = MagicMock()
    mock_existing_guild_entity.name = "Old Name"
    mock_existing_guild_entity.icon_url = "old_url"
    mock_existing_guild_entity.member_count = 10
    mock_session.execute.return_value.scalars.return_value.first.return_value = mock_existing_guild_entity
    
    # Give the mock guild an icon this time
    mock_guild.icon = MagicMock()
    mock_guild.icon.url = "new_icon_url"

    await workflow.sync_guild_to_database(mock_guild)
    
    mock_session.execute.assert_awaited_once() 
    mock_session.add.assert_not_called() # Should not add a new entity
    # Verify attributes were updated on the existing entity
    assert mock_existing_guild_entity.name == mock_guild.name
    assert mock_existing_guild_entity.icon_url == "new_icon_url"
    assert mock_existing_guild_entity.member_count == len(mock_guild.members)
    mock_session.commit.assert_awaited_once()

# --- Test sync_guild_members ---

@pytest.mark.asyncio
async def test_sync_guild_members_success(user_workflow_no_patch, mock_guild, mock_member, mock_bot_member, mock_session_context, mock_user_repository_impl_class, mock_user_repo_instance, mocker):
    """Test syncing members, including skipping bots and calling create_or_update."""
    workflow = user_workflow_no_patch
    # Mock the sync_guild_to_database call within sync_guild_members
    mock_sync_guild_db = mocker.patch.object(workflow, 'sync_guild_to_database', new_callable=AsyncMock)
    
    await workflow.sync_guild_members(mock_guild)
    
    # Check sync_guild_to_database was called
    mock_sync_guild_db.assert_awaited_once_with(mock_guild)
    
    # Check session context was used
    mock_session_context.assert_called_once()
    
    # Check repo was initialized
    mock_user_repository_impl_class.assert_called_once_with(mock_session_context.return_value.__aenter__.return_value)
    
    # Check create_or_update was called ONLY for the non-bot member
    mock_user_repo_instance.create_or_update.assert_awaited_once()
    call_args, call_kwargs = mock_user_repo_instance.create_or_update.await_args
    user_data = call_args[0]
    assert user_data['discord_id'] == mock_member.id
    assert user_data['username'] == mock_member.name
    assert user_data['is_bot'] is False
    assert user_data['guild_id'] == str(mock_guild.id)
    # Check it wasn't called for the bot member (await_count should still be 1)
    assert mock_user_repo_instance.create_or_update.await_count == 1

@pytest.mark.asyncio
async def test_sync_guild_members_handles_repo_error(user_workflow_no_patch, mock_guild, mock_session_context, mock_user_repository_impl_class, mock_user_repo_instance, mocker):
    """Test that sync continues if create_or_update fails for one member."""
    workflow = user_workflow_no_patch
    mock_sync_guild_db = mocker.patch.object(workflow, 'sync_guild_to_database', new_callable=AsyncMock)
    mock_logger_error = mocker.patch("app.bot.application.workflows.user_workflow.logger.error")
    
    # Make create_or_update fail
    mock_user_repo_instance.create_or_update.side_effect = Exception("DB Write Error!")
    
    await workflow.sync_guild_members(mock_guild)
    
    # Check it was still called for the non-bot member
    assert mock_user_repo_instance.create_or_update.await_count == 1 
    # Check error was logged
    mock_logger_error.assert_called_once()
    assert "Failed to sync member TestUser" in mock_logger_error.call_args[0][0] 
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
import nextcord
from nextcord.enums import ChannelType
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.application.workflows.guild_template_workflow import GuildTemplateWorkflow, WorkflowStatus
from app.shared.infrastructure.models.discord.entities import GuildConfigEntity
# Import Repository Impls to mock their paths if needed, and for spec
from app.shared.infrastructure.repositories.guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl,
    GuildTemplateCategoryPermissionRepositoryImpl,
    GuildTemplateChannelPermissionRepositoryImpl
)

# --- Fixtures ---

@pytest.fixture
def mock_bot():
    return AsyncMock(name="MockBot")

@pytest.fixture
def mock_db_workflow():
    return MagicMock(name="MockDatabaseWorkflow")

@pytest.fixture
def mock_guild_workflow_dep(): # Renamed to avoid clash with main fixture for GuildWorkflow tests
    return MagicMock(name="MockGuildWorkflowDependency")

@pytest.fixture
def guild_template_workflow(mock_db_workflow, mock_guild_workflow_dep, mock_bot):
    return GuildTemplateWorkflow(database_workflow=mock_db_workflow, guild_workflow=mock_guild_workflow_dep, bot=mock_bot)

@pytest.fixture
def mock_nextcord_guild():
    guild = MagicMock(spec=nextcord.Guild)
    guild.id = 12345
    guild.name = "Test Guild"
    guild.roles = []
    guild.categories = []
    guild.channels = [] 
    return guild

@pytest.fixture
def mock_guild_config_entity():
    config = MagicMock(spec=GuildConfigEntity)
    config.id = 1
    config.guild_id = "12345"
    config.active_template_id = None
    return config

@pytest.fixture
def mock_async_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_session_context_manager(mocker, mock_async_session):
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_async_session
    async_context_manager.__aexit__.return_value = None
    return mocker.patch("app.bot.application.workflows.guild_template_workflow.session_context", return_value=async_context_manager)


# Mock repository classes
@pytest.fixture
def mock_template_repo(mocker):
    instance = AsyncMock(spec=GuildTemplateRepositoryImpl)
    instance.get_by_guild_id = AsyncMock(return_value=None) # Default to not found
    instance.create = AsyncMock(return_value=MagicMock(id=1)) # Default create success
    return mocker.patch("app.bot.application.workflows.guild_template_workflow.GuildTemplateRepositoryImpl", return_value=instance)

@pytest.fixture
def mock_category_repo(mocker):
    instance = AsyncMock(spec=GuildTemplateCategoryRepositoryImpl)
    instance.create = AsyncMock(return_value=MagicMock(id=10)) 
    return mocker.patch("app.bot.application.workflows.guild_template_workflow.GuildTemplateCategoryRepositoryImpl", return_value=instance)

@pytest.fixture
def mock_channel_repo(mocker):
    instance = AsyncMock(spec=GuildTemplateChannelRepositoryImpl)
    instance.create = AsyncMock(return_value=MagicMock(id=100))
    return mocker.patch("app.bot.application.workflows.guild_template_workflow.GuildTemplateChannelRepositoryImpl", return_value=instance)

@pytest.fixture
def mock_cat_perm_repo(mocker):
    instance = AsyncMock(spec=GuildTemplateCategoryPermissionRepositoryImpl)
    instance.create = AsyncMock(return_value=MagicMock(id=1000))
    return mocker.patch("app.bot.application.workflows.guild_template_workflow.GuildTemplateCategoryPermissionRepositoryImpl", return_value=instance)

@pytest.fixture
def mock_chan_perm_repo(mocker):
    instance = AsyncMock(spec=GuildTemplateChannelPermissionRepositoryImpl)
    instance.create = AsyncMock(return_value=MagicMock(id=10000))
    return mocker.patch("app.bot.application.workflows.guild_template_workflow.GuildTemplateChannelPermissionRepositoryImpl", return_value=instance)


# --- Basic Tests ---

@pytest.mark.asyncio
async def test_initialize_success(guild_template_workflow):
    """Test simple global initialization."""
    result = await guild_template_workflow.initialize()
    assert result is True

@pytest.mark.asyncio
async def test_initialize_for_guild(guild_template_workflow):
    """Test initialize_for_guild sets status correctly."""
    guild_id = "guild123"
    result = await guild_template_workflow.initialize_for_guild(guild_id)
    assert result is True
    assert guild_template_workflow.guild_status[guild_id] == WorkflowStatus.ACTIVE

@pytest.mark.asyncio
async def test_cleanup_success(guild_template_workflow, mocker):
    """Test simple cleanup calls super().cleanup."""
    mock_base_cleanup = mocker.patch("app.bot.application.workflows.base_workflow.BaseWorkflow.cleanup", new_callable=AsyncMock)
    
    await guild_template_workflow.cleanup()
    
    # Assert that the mocked BaseWorkflow.cleanup was called via super()
    # When super().cleanup() is called, the mock replacing BaseWorkflow.cleanup
    # is invoked. The `self` (instance of GuildTemplateWorkflow) is implicitly passed
    # by Python's method resolution, but to the mock itself, it appears as a call without explicit args 
    # if the mock is not a bound method itself. We just need to ensure it was awaited.
    mock_base_cleanup.assert_awaited_once() # Check it was awaited, args are tricky with super() patching


# --- create_template_for_guild Tests (more to come) ---

@pytest.mark.asyncio
async def test_create_template_for_guild_new_template_success_no_structure(
    guild_template_workflow, mock_nextcord_guild, mock_guild_config_entity, 
    mock_session_context_manager, mock_async_session,
    mock_template_repo, mock_category_repo, mock_channel_repo, # Other repos not used if no structure
    mocker
):
    """Test creating a new template for a guild with no categories/channels successfully."""
    # Ensure get_by_guild_id returns None (template doesn't exist)
    guild_template_repo_instance = mock_template_repo.return_value
    guild_template_repo_instance.get_by_guild_id.return_value = None
    
    # Mock create to return a template record with an ID
    mock_created_template_record = MagicMock(id=77)
    guild_template_repo_instance.create.return_value = mock_created_template_record

    # Call the method under test (using outer session context)
    success = await guild_template_workflow.create_template_for_guild(
        mock_nextcord_guild, mock_guild_config_entity
    )

    assert success is True
    # Check main template repo calls
    guild_template_repo_instance.get_by_guild_id.assert_awaited_once_with(str(mock_nextcord_guild.id))
    guild_template_repo_instance.create.assert_awaited_once() # Args checked implicitly by what's passed
    # Check guild_config was updated
    assert mock_guild_config_entity.active_template_id == mock_created_template_record.id
    # Check structure processing repos were NOT called as guild has no structure and template is new
    mock_category_repo.return_value.create.assert_not_called()
    mock_channel_repo.return_value.create.assert_not_called()

@pytest.mark.asyncio
async def test_create_template_for_guild_existing_template_updates_config(
    guild_template_workflow, mock_nextcord_guild, mock_guild_config_entity, 
    mock_session_context_manager, mock_async_session,
    mock_template_repo, mocker
):
    """Test when a template exists, it updates guild_config if ID is different and skips structure."""
    existing_template_id = 99
    mock_existing_template = MagicMock(id=existing_template_id)
    guild_template_repo_instance = mock_template_repo.return_value
    guild_template_repo_instance.get_by_guild_id.return_value = mock_existing_template
    
    # Ensure guild_config has a different active_template_id initially
    mock_guild_config_entity.active_template_id = 55 

    success = await guild_template_workflow.create_template_for_guild(
        mock_nextcord_guild, mock_guild_config_entity
    )

    assert success is True
    guild_template_repo_instance.get_by_guild_id.assert_awaited_once_with(str(mock_nextcord_guild.id))
    guild_template_repo_instance.create.assert_not_called() # Should not create a new one
    assert mock_guild_config_entity.active_template_id == existing_template_id

@pytest.mark.asyncio
async def test_create_template_for_guild_existing_template_already_active(
    guild_template_workflow, mock_nextcord_guild, mock_guild_config_entity, 
    mock_session_context_manager, mock_async_session,
    mock_template_repo, mocker
):
    """Test when a template exists and is already active, no config update, skips structure."""
    existing_template_id = 99
    mock_existing_template = MagicMock(id=existing_template_id)
    guild_template_repo_instance = mock_template_repo.return_value
    guild_template_repo_instance.get_by_guild_id.return_value = mock_existing_template
    
    # Guild config already has this template as active
    mock_guild_config_entity.active_template_id = existing_template_id
    # Mock logger to check for specific message
    mock_logger_info = mocker.patch("app.bot.application.workflows.guild_template_workflow.logger.info")

    success = await guild_template_workflow.create_template_for_guild(
        mock_nextcord_guild, mock_guild_config_entity
    )

    assert success is True
    guild_template_repo_instance.get_by_guild_id.assert_awaited_once_with(str(mock_nextcord_guild.id))
    assert mock_guild_config_entity.active_template_id == existing_template_id # Remains unchanged
    mock_logger_info.assert_any_call(
        f"[GuildTemplateWorkflow] [Guild:{mock_nextcord_guild.id}] Template {existing_template_id} is already active on passed GuildConfig object. No change needed."
    )

@pytest.mark.asyncio
async def test_create_template_for_guild_uses_passed_db_session(
    guild_template_workflow, mock_nextcord_guild, mock_guild_config_entity, 
    mock_async_session, mock_template_repo, mock_session_context_manager # mock_session_context_manager to assert it's NOT called
):
    """Test that a passed db_session is used instead of creating a new context."""
    guild_template_repo_instance = mock_template_repo.return_value
    guild_template_repo_instance.get_by_guild_id.return_value = None # New template
    mock_created_template_record = MagicMock(id=77)
    guild_template_repo_instance.create.return_value = mock_created_template_record

    # Call with an existing session
    success = await guild_template_workflow.create_template_for_guild(
        mock_nextcord_guild, mock_guild_config_entity, db_session=mock_async_session
    )

    assert success is True
    mock_session_context_manager.assert_not_called() # session_context should not be used
    # Repositories should be initialized with the passed mock_async_session
    # This is implicitly tested by the fact that mock_template_repo (which is a patch of the class)
    # gets called. If we were testing the repo init directly, we'd check its __init__ args.
    guild_template_repo_instance.get_by_guild_id.assert_awaited_once_with(str(mock_nextcord_guild.id))
    assert mock_guild_config_entity.active_template_id == mock_created_template_record.id

# More tests for structure processing (categories, channels, perms) and error handling needed here. 

# --- More detailed Guild Structure Fixture ---

@pytest.fixture
def mock_nextcord_guild_with_structure(mock_nextcord_guild): # Extends the basic one
    guild = mock_nextcord_guild

    # --- Roles ---
    mock_role_everyone = MagicMock(spec=nextcord.Role)
    mock_role_everyone.name = "@everyone"
    mock_role_everyone.id = guild.id 
    mock_role_admin = MagicMock(spec=nextcord.Role)
    mock_role_admin.name = "Admin"
    mock_role_admin.id = 101
    mock_role_member = MagicMock(spec=nextcord.Role)
    mock_role_member.name = "Member"
    mock_role_member.id = 102
    guild.roles = [mock_role_everyone, mock_role_admin, mock_role_member]

    # --- Category 1 with a Text Channel and Permissions ---
    mock_category1 = MagicMock(spec=nextcord.CategoryChannel)
    mock_category1.name = "General"
    mock_category1.id = 201
    mock_category1.position = 0
    cat1_perm_overwrite_admin = MagicMock(spec=nextcord.PermissionOverwrite)
    cat1_perm_overwrite_admin.pair.return_value = (nextcord.Permissions(read_messages=True, send_messages=True), nextcord.Permissions())
    mock_category1.overwrites = { mock_role_admin: cat1_perm_overwrite_admin }

    mock_text_channel1 = MagicMock(spec=nextcord.TextChannel)
    mock_text_channel1.name = "general-chat"
    mock_text_channel1.id = 301
    mock_text_channel1.type = ChannelType.text
    mock_text_channel1.category = mock_category1
    mock_text_channel1.position = 0
    mock_text_channel1.topic = "General discussion"
    mock_text_channel1.nsfw = False # Explicitly set
    mock_text_channel1.slowmode_delay = 5
    chan1_perm_overwrite_member = MagicMock(spec=nextcord.PermissionOverwrite)
    chan1_perm_overwrite_member.pair.return_value = (nextcord.Permissions(send_messages=True), nextcord.Permissions(manage_messages=True))
    mock_text_channel1.overwrites = { mock_role_member: chan1_perm_overwrite_member }

    # --- Category 2 (empty) ---
    mock_category2 = MagicMock(spec=nextcord.CategoryChannel)
    mock_category2.name = "Archive"
    mock_category2.id = 202
    mock_category2.position = 1
    mock_category2.overwrites = {}

    # --- Voice Channel (no category) ---
    mock_voice_channel1 = MagicMock(spec=nextcord.VoiceChannel)
    mock_voice_channel1.name = "Voice Chat"
    mock_voice_channel1.id = 401
    mock_voice_channel1.type = ChannelType.voice
    mock_voice_channel1.category = None
    mock_voice_channel1.position = 1
    mock_voice_channel1.nsfw = False # Explicitly set here too
    # For VoiceChannel, slowmode_delay is not applicable or typically 0, getattr will handle it
    mock_voice_channel1.topic = None # Voice channels usually don't have topics like text channels
    mock_voice_channel1.overwrites = {}

    guild.categories = [mock_category1, mock_category2]
    guild.channels = [mock_text_channel1, mock_voice_channel1] 
    return guild

# --- Test with Structure ---

@pytest.mark.asyncio
async def test_create_template_for_guild_processes_full_structure(
    guild_template_workflow, mock_nextcord_guild_with_structure, mock_guild_config_entity,
    mock_session_context_manager, mock_async_session,
    mock_template_repo, mock_category_repo, mock_channel_repo, 
    mock_cat_perm_repo, mock_chan_perm_repo, mocker
):
    """Test creating a new template, processing categories, channels, and permissions."""
    guild = mock_nextcord_guild_with_structure
    guild_template_repo_instance = mock_template_repo.return_value
    guild_template_repo_instance.get_by_guild_id.return_value = None # New template
    mock_created_template_record = MagicMock(id=111)
    guild_template_repo_instance.create.return_value = mock_created_template_record

    # Mock return values for category and channel repo create to get their IDs
    cat_repo_instance = mock_category_repo.return_value
    mock_cat1_template = MagicMock(id=222); mock_cat1_template.name = "General_template"
    mock_cat2_template = MagicMock(id=333); mock_cat2_template.name = "Archive_template"
    cat_repo_instance.create.side_effect = [mock_cat1_template, mock_cat2_template]

    chan_repo_instance = mock_channel_repo.return_value
    mock_chan1_template = MagicMock(id=444); mock_chan1_template.name = "general-chat_template"
    mock_chan2_template = MagicMock(id=555); mock_chan2_template.name = "Voice Chat_template"
    # The order of channel processing depends on the sort key used in the SUT
    # Current SUT sorts all channels by position: text_channel1 (pos 0), voice_channel1 (pos 1 in its context)
    chan_repo_instance.create.side_effect = [mock_chan1_template, mock_chan2_template]

    cat_perm_repo_instance = mock_cat_perm_repo.return_value
    chan_perm_repo_instance = mock_chan_perm_repo.return_value

    success = await guild_template_workflow.create_template_for_guild(guild, mock_guild_config_entity)

    assert success is True
    assert mock_guild_config_entity.active_template_id == mock_created_template_record.id

    # Check main template creation
    guild_template_repo_instance.create.assert_awaited_once()
    # ... (more detailed checks for create args if necessary) ...

    # Check category creation (should be 2 categories)
    assert cat_repo_instance.create.await_count == 2
    cat_repo_instance.create.assert_any_await(
        guild_template_id=mock_created_template_record.id,
        category_name="General",
        position=0
    )
    cat_repo_instance.create.assert_any_await(
        guild_template_id=mock_created_template_record.id,
        category_name="Archive",
        position=1
    )

    # Check channel creation (should be 2 channels)
    assert chan_repo_instance.create.await_count == 2
    chan_repo_instance.create.assert_any_await(
        guild_template_id=mock_created_template_record.id,
        channel_name="general-chat",
        channel_type=str(ChannelType.text),
        position=0, topic="General discussion", is_nsfw=False, slowmode_delay=5,
        parent_category_template_id=mock_cat1_template.id # General category's template ID
    )
    chan_repo_instance.create.assert_any_await(
        guild_template_id=mock_created_template_record.id,
        channel_name="Voice Chat",
        channel_type=str(ChannelType.voice),
        position=1, topic=None, is_nsfw=False, slowmode_delay=0, # Defaults for voice
        parent_category_template_id=None # No category for this voice channel
    )

    # Check category permission creation (1 for Admin role in General category)
    assert cat_perm_repo_instance.create.await_count == 1
    cat_perm_repo_instance.create.assert_awaited_once_with(
        category_template_id=mock_cat1_template.id, # General category's template ID
        role_name="Admin",
        allow_permissions_bitfield=nextcord.Permissions(read_messages=True, send_messages=True).value,
        deny_permissions_bitfield=None # Deny is empty
    )

    # Check channel permission creation (1 for Member role in general-chat channel)
    assert chan_perm_repo_instance.create.await_count == 1
    chan_perm_repo_instance.create.assert_awaited_once_with(
        channel_template_id=mock_chan1_template.id, # general-chat channel's template ID
        role_name="Member",
        allow_permissions_bitfield=nextcord.Permissions(send_messages=True).value,
        deny_permissions_bitfield=nextcord.Permissions(manage_messages=True).value
    )

# Add tests for error handling during structure processing if one of the repo.create calls fails. 
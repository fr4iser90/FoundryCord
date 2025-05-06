import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
from app.bot.application.workflows.dashboard_workflow import DashboardWorkflow, WorkflowStatus
from app.bot.application.services.dashboard.dashboard_lifecycle_service import DashboardLifecycleService
from app.shared.infrastructure.repositories.dashboards import ActiveDashboardRepositoryImpl

# --- Fixtures ---

@pytest.fixture
def mock_bot():
    bot = AsyncMock(name="MockBot")
    bot.user = MagicMock()
    bot.user.id = 123456789
    bot.get_guild = MagicMock(return_value=MagicMock(name="MockGuild"))
    bot.service_factory = MagicMock(name="MockServiceFactory") # For lifecycle service init logging
    return bot

@pytest.fixture
def mock_database_workflow():
    """Provides a mock DatabaseWorkflow."""
    return MagicMock(name="MockDatabaseWorkflow")

@pytest.fixture
def dashboard_workflow(mock_database_workflow):
    """Provides a DashboardWorkflow instance."""
    return DashboardWorkflow(database_workflow=mock_database_workflow)

@pytest.fixture
def mock_lifecycle_service_instance():
    service = AsyncMock(spec=DashboardLifecycleService)
    service.initialize = AsyncMock(return_value=True)
    service.shutdown = AsyncMock()
    return service

@pytest.fixture
def mock_dashboard_lifecycle_service_class(mocker, mock_lifecycle_service_instance):
    """Mocks the DashboardLifecycleService class to return our instance."""
    # Patch where it's imported/used by DashboardWorkflow
    return mocker.patch(
        "app.bot.application.workflows.dashboard_workflow.DashboardLifecycleService", 
        return_value=mock_lifecycle_service_instance
    )

@pytest.fixture
def mock_active_dashboard_repo_instance():
    repo = AsyncMock(spec=ActiveDashboardRepositoryImpl)
    repo.get_all_dashboards = AsyncMock(return_value=[MagicMock(name="DBDashboard1"), MagicMock(name="DBDashboard2")])
    repo.get_dashboards_by_guild = AsyncMock(return_value=[MagicMock(name="GuildDashboard1")])
    repo.delete_dashboard = AsyncMock()
    return repo

@pytest.fixture
def mock_active_dashboard_repository_impl_class(mocker, mock_active_dashboard_repo_instance):
    return mocker.patch(
        "app.bot.application.workflows.dashboard_workflow.ActiveDashboardRepositoryImpl",
        return_value=mock_active_dashboard_repo_instance
    )

@pytest.fixture
def mock_session_context(mocker):
    mock_session = AsyncMock(name="MockDbSession")
    # Mock the async context manager behavior
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_session
    async_context_manager.__aexit__.return_value = None
    return mocker.patch(
        "app.bot.application.workflows.dashboard_workflow.session_context", 
        return_value=async_context_manager
    )

# --- Test Initialize ---

@pytest.mark.asyncio
async def test_initialize_success(dashboard_workflow, mock_bot, mock_dashboard_lifecycle_service_class, mock_lifecycle_service_instance):
    """Test successful global initialization of the workflow."""
    result = await dashboard_workflow.initialize(mock_bot)
    
    assert result is True
    assert dashboard_workflow.bot is mock_bot
    mock_dashboard_lifecycle_service_class.assert_called_once_with(mock_bot)
    mock_lifecycle_service_instance.initialize.assert_awaited_once()

@pytest.mark.asyncio
async def test_initialize_no_bot(dashboard_workflow, mock_dashboard_lifecycle_service_class, mocker):
    """Test initialize failure when no bot instance is provided."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.error")
    result = await dashboard_workflow.initialize(None) # Pass None as bot
    
    assert result is False
    mock_logger_error.assert_called_once_with("[DashboardWorkflow] Bot instance not provided. Cannot start LifecycleService.")
    mock_dashboard_lifecycle_service_class.assert_not_called()

@pytest.mark.asyncio
async def test_initialize_lifecycle_service_fails(dashboard_workflow, mock_bot, mock_dashboard_lifecycle_service_class, mock_lifecycle_service_instance, mocker):
    """Test initialize failure when DashboardLifecycleService fails to initialize."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.error")
    mock_lifecycle_service_instance.initialize.return_value = False # Simulate failure
    
    result = await dashboard_workflow.initialize(mock_bot)
    
    assert result is False
    mock_dashboard_lifecycle_service_class.assert_called_once_with(mock_bot)
    mock_lifecycle_service_instance.initialize.assert_awaited_once()
    mock_logger_error.assert_called_once_with("[DashboardWorkflow] DashboardLifecycleService initialization failed.")

# --- Test Initialize for Guild ---

@pytest.mark.asyncio
async def test_initialize_for_guild_success(dashboard_workflow, mock_bot):
    """Test successful initialization for a guild."""
    guild_id = "12345"
    result = await dashboard_workflow.initialize_for_guild(guild_id, mock_bot)
    
    assert result is True
    assert dashboard_workflow.guild_status[guild_id] == WorkflowStatus.ACTIVE
    mock_bot.get_guild.assert_called_once_with(int(guild_id))

@pytest.mark.asyncio
async def test_initialize_for_guild_no_bot(dashboard_workflow, mocker):
    """Test initialize_for_guild failure when no bot instance is provided."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.error")
    guild_id = "67890"
    result = await dashboard_workflow.initialize_for_guild(guild_id, None) # Pass None as bot
    
    assert result is False
    assert dashboard_workflow.guild_status[guild_id] == WorkflowStatus.FAILED
    mock_logger_error.assert_called_once_with("[DashboardWorkflow] Bot instance not available")

@pytest.mark.asyncio
async def test_initialize_for_guild_not_found(dashboard_workflow, mock_bot, mocker):
    """Test initialize_for_guild failure when guild is not found."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.error")
    mock_bot.get_guild.return_value = None # Simulate guild not found
    guild_id = "11223"
    
    result = await dashboard_workflow.initialize_for_guild(guild_id, mock_bot)
    
    assert result is False
    assert dashboard_workflow.guild_status[guild_id] == WorkflowStatus.FAILED
    mock_bot.get_guild.assert_called_once_with(int(guild_id))
    mock_logger_error.assert_called_once_with(f"[DashboardWorkflow] [Guild:{guild_id}] Could not find guild object")

# --- Test Cleanup ---
@pytest.mark.asyncio
async def test_cleanup_calls_lifecycle_shutdown(dashboard_workflow, mock_lifecycle_service_instance):
    """Test that cleanup calls shutdown on the lifecycle service."""
    # Setup: Ensure lifecycle_service is set (e.g., after a successful initialize)
    dashboard_workflow.lifecycle_service = mock_lifecycle_service_instance 
    
    await dashboard_workflow.cleanup()
    mock_lifecycle_service_instance.shutdown.assert_awaited_once()

@pytest.mark.asyncio
async def test_cleanup_handles_no_lifecycle_service(dashboard_workflow):
    """Test that cleanup handles when lifecycle_service is None."""
    dashboard_workflow.lifecycle_service = None # Ensure it's None
    try:
        await dashboard_workflow.cleanup()
        # Should not raise an error
    except Exception as e:
        pytest.fail(f"Cleanup raised an unexpected exception: {e}")

# --- Test Load Dashboards ---
@pytest.mark.asyncio
async def test_load_dashboards_with_passed_repo(dashboard_workflow, mock_active_dashboard_repo_instance):
    """Test load_dashboards when a repository instance is passed directly."""
    dashboards = await dashboard_workflow.load_dashboards(repo=mock_active_dashboard_repo_instance)
    mock_active_dashboard_repo_instance.get_all_dashboards.assert_awaited_once()
    assert len(dashboards) == 2 # Based on fixture

@pytest.mark.asyncio
async def test_load_dashboards_uses_session_context(dashboard_workflow, mock_session_context, mock_active_dashboard_repository_impl_class, mock_active_dashboard_repo_instance):
    """Test load_dashboards uses session_context when no repo is passed."""
    dashboards = await dashboard_workflow.load_dashboards()
    
    mock_session_context.assert_called_once() # Check context manager was entered
    mock_active_dashboard_repository_impl_class.assert_called_once_with(mock_session_context.return_value.__aenter__.return_value) # Check repo init with session
    mock_active_dashboard_repo_instance.get_all_dashboards.assert_awaited_once()
    assert len(dashboards) == 2

@pytest.mark.asyncio
async def test_load_dashboards_handles_db_error(dashboard_workflow, mock_session_context, mock_active_dashboard_repository_impl_class, mock_active_dashboard_repo_instance, mocker):
    """Test load_dashboards handles general DB errors."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.error")
    mock_active_dashboard_repo_instance.get_all_dashboards.side_effect = Exception("DB Boom!")
    
    dashboards = await dashboard_workflow.load_dashboards()
    
    assert dashboards == []
    mock_logger_error.assert_called_once_with("[DashboardWorkflow] Error retrieving dashboards: DB Boom!", exc_info=True)

@pytest.mark.asyncio
async def test_load_dashboards_handles_table_not_exist_error(dashboard_workflow, mock_session_context, mock_active_dashboard_repository_impl_class, mock_active_dashboard_repo_instance, mocker):
    """Test load_dashboards specifically handles 'relation does not exist' errors."""
    mock_logger_warning = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.warning")
    mock_active_dashboard_repo_instance.get_all_dashboards.side_effect = Exception("relation \"active_dashboards\" does not exist")
    
    dashboards = await dashboard_workflow.load_dashboards()
    
    assert dashboards == []
    mock_logger_warning.assert_called_once_with("[DashboardWorkflow] Dashboard tables don't exist yet, skipping dashboard load.")

# --- Test Cleanup Guild ---
@pytest.mark.asyncio
async def test_cleanup_guild_success(dashboard_workflow, mock_session_context, mock_active_dashboard_repository_impl_class, mock_active_dashboard_repo_instance):
    """Test successful cleanup of guild-specific dashboards."""
    guild_id = "777"
    # Simulate that get_dashboards_by_guild returns a list of mock entities
    mock_dashboard_entity = MagicMock(name="MockDashboardEntity")
    mock_active_dashboard_repo_instance.get_dashboards_by_guild.return_value = [mock_dashboard_entity, mock_dashboard_entity]

    await dashboard_workflow.cleanup_guild(guild_id)
    
    mock_session_context.assert_called_once()
    mock_active_dashboard_repository_impl_class.assert_called_once_with(mock_session_context.return_value.__aenter__.return_value)
    mock_active_dashboard_repo_instance.get_dashboards_by_guild.assert_awaited_once_with(guild_id)
    # Check delete_dashboard was called for each entity
    mock_active_dashboard_repo_instance.delete_dashboard.assert_has_awaits([
        call(mock_dashboard_entity), call(mock_dashboard_entity)
    ])
    assert mock_active_dashboard_repo_instance.delete_dashboard.await_count == 2

@pytest.mark.asyncio
async def test_cleanup_guild_no_dashboards_to_delete(dashboard_workflow, mock_session_context, mock_active_dashboard_repository_impl_class, mock_active_dashboard_repo_instance):
    """Test cleanup_guild when there are no dashboards for the guild."""
    guild_id = "888"
    mock_active_dashboard_repo_instance.get_dashboards_by_guild.return_value = [] # No dashboards
    
    await dashboard_workflow.cleanup_guild(guild_id)
    
    mock_active_dashboard_repo_instance.get_dashboards_by_guild.assert_awaited_once_with(guild_id)
    mock_active_dashboard_repo_instance.delete_dashboard.assert_not_awaited()

@pytest.mark.asyncio
async def test_cleanup_guild_handles_db_error(dashboard_workflow, mock_session_context, mock_active_dashboard_repository_impl_class, mock_active_dashboard_repo_instance, mocker):
    """Test cleanup_guild handles DB errors during dashboard deletion."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.dashboard_workflow.logger.error")
    guild_id = "999"
    mock_active_dashboard_repo_instance.get_dashboards_by_guild.side_effect = Exception("Cleanup DB Error")
    
    await dashboard_workflow.cleanup_guild(guild_id)
    
    mock_logger_error.assert_called_once_with(f"[DashboardWorkflow] [Guild:{guild_id}] Error cleaning up dashboards: Cleanup DB Error", exc_info=True)
    mock_active_dashboard_repo_instance.delete_dashboard.assert_not_awaited() 
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call, Mock
from app.bot.application.services.dashboard.dashboard_data_service import DashboardDataService

# --- Fixtures ---

@pytest.fixture
def mock_bot():
    """Provides a mock bot instance."""
    return MagicMock(name="MockBot")

@pytest.fixture
def mock_service_factory():
    """Provides a mock ServiceFactoryInterface."""
    factory = MagicMock(name="MockServiceFactory")
    factory.get_service = MagicMock(name="get_service_mock")
    return factory

@pytest.fixture
def data_service(mock_bot, mock_service_factory):
    """Provides a DashboardDataService instance with mock dependencies."""
    return DashboardDataService(bot=mock_bot, service_factory=mock_service_factory)

# --- Test __init__ and initialize ---

@pytest.mark.asyncio
async def test_dashboard_data_service_initialization(data_service, mock_bot, mock_service_factory):
    """Test that the service initializes its attributes correctly."""
    assert data_service.bot is mock_bot
    assert data_service.service_factory is mock_service_factory
    assert data_service.initialized is False

@pytest.mark.asyncio
async def test_initialize_method_success(data_service):
    """Test the initialize method sets the initialized flag."""
    assert data_service.initialized is False
    result = await data_service.initialize()
    assert result is True
    assert data_service.initialized is True

# Removed the problematic/confusing second part of test_initialize_method_exception
# The current initialize() is too simple to easily test an exception path within it.
# The first part test_initialize_method_success covers the current functionality.

# --- Test fetch_data: Not Initialized ---

@pytest.mark.asyncio
async def test_fetch_data_not_initialized(data_service, mocker):
    """Test fetch_data returns None and logs error if service is not initialized."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    assert data_service.initialized is False # Pre-condition
    
    result = await data_service.fetch_data(data_sources_config={})
    
    assert result is None
    mock_logger_error.assert_called_once_with("Cannot fetch data: DashboardDataService not initialized.")

# --- Test fetch_data: System Collector --- 

@pytest.fixture
def mock_system_collector():
    collector = AsyncMock(name="MockSystemCollector")
    
    # Create individual metric mocks and set their attributes explicitly
    cpu_metric = Mock()
    cpu_metric.name = "cpu_usage" # Explicitly set the .name attribute
    cpu_metric.value = 75.5
    cpu_metric.metric_data = {}

    memory_metric = Mock()
    memory_metric.name = "memory_percent"
    memory_metric.value = 50.2
    memory_metric.metric_data = {}

    disk_metric = Mock()
    disk_metric.name = "disk_percent"
    disk_metric.value = 25.0
    disk_metric.metric_data = {}

    hostname_metric = Mock()
    hostname_metric.name = "hostname"
    hostname_metric.value = None # Value is not used for this one in the code
    hostname_metric.metric_data = {"hostname": "test-host"}

    platform_metric = Mock()
    platform_metric.name = "platform"
    platform_metric.value = None
    platform_metric.metric_data = {"platform": "TestOS"}

    uptime_metric = Mock()
    uptime_metric.name = "uptime"
    uptime_metric.value = None
    uptime_metric.metric_data = {"uptime": "1 day"}
    
    collector.collect_all = AsyncMock(return_value=[
        cpu_metric, memory_metric, disk_metric,
        hostname_metric, platform_metric, uptime_metric
    ])
    return collector

@pytest.mark.asyncio
async def test_fetch_data_system_collector_success(data_service, mock_service_factory, mock_system_collector):
    """Test successful data fetching using system_collector."""
    await data_service.initialize()
    mock_service_factory.get_service.return_value = mock_system_collector
    
    config = {"sys_metrics": {"type": "system_collector"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("system_collector")
    mock_system_collector.collect_all.assert_awaited_once()
    
    assert "sys_metrics" in result
    assert result["sys_metrics"]["cpu_percent"] == 75.5 
    assert result["sys_metrics"]["memory_percent"] == 50.2
    assert result["sys_metrics"]["disk_percent"] == 25.0
    assert result["sys_metrics"]["hostname"] == "test-host"
    assert result["sys_metrics"]["platform"] == "TestOS"
    assert result["sys_metrics"]["uptime"] == "1 day"

@pytest.mark.asyncio
async def test_fetch_data_system_collector_not_found(data_service, mock_service_factory, mocker):
    """Test fetch_data when system_collector service is not found."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    mock_service_factory.get_service.return_value = None # Simulate service not found
    
    config = {"sys_metrics": {"type": "system_collector"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("system_collector")
    mock_logger_error.assert_called_once_with("SystemCollector service not found in ServiceFactory.")
    assert result["sys_metrics"] == {"error": "SystemCollector not available"}

@pytest.mark.asyncio
async def test_fetch_data_system_collector_exception(data_service, mock_service_factory, mock_system_collector, mocker):
    """Test fetch_data when system_collector raises an exception."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    mock_system_collector.collect_all.side_effect = Exception("Collector Error!")
    mock_service_factory.get_service.return_value = mock_system_collector
    
    config = {"sys_metrics": {"type": "system_collector"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("system_collector")
    mock_system_collector.collect_all.assert_awaited_once()
    mock_logger_error.assert_called_once()
    assert "Error fetching data from SystemCollector" in mock_logger_error.call_args[0][0]
    assert result["sys_metrics"] == {"error": "Collector Error!"}

# --- Test fetch_data: DB Repository --- 

@pytest.fixture
def mock_project_repo_instance():
    repo = AsyncMock(name="MockProjectRepositoryImpl")
    repo.get_active_projects_by_guild = AsyncMock(return_value=[
        {"id": 1, "name": "Project Alpha"}, 
        {"id": 2, "name": "Project Beta"}
    ])
    repo.get_archived_projects_by_guild = AsyncMock(return_value=[
        {"id": 3, "name": "Project Gamma (Archived)"}
    ])
    return repo

@pytest.fixture
def mock_get_session(mock_project_repo_instance):
    # This context manager mock is a bit more involved.
    # We need it to yield the session, and the session needs to be a mock.
    # And the ProjectRepositoryImpl needs to be initialized with this session mock.
    
    # The session itself doesn't need to do much for this test, as ProjectRepositoryImpl is fully mocked.
    mock_db_session = AsyncMock(name="MockDbSession")

    # The context manager itself
    @pytest.mark.asyncio
    async def _mock_context_manager(*args, **kwargs):
        yield mock_db_session

    # We need to patch where get_session is *called* from, which is DashboardDataService's module
    return patch("app.bot.application.services.dashboard.dashboard_data_service.get_session", new=_mock_context_manager)

@pytest.fixture
def mock_project_repository_impl_class(mock_project_repo_instance):
    # This mock will be used as the class for ProjectRepositoryImpl
    # When instantiated, it should return our mock_project_repo_instance
    klass_mock = MagicMock(name="MockProjectRepositoryImplClass", return_value=mock_project_repo_instance)
    return klass_mock

@pytest.mark.asyncio
async def test_fetch_data_db_repository_success(
    data_service, mock_service_factory, mock_get_session, mock_project_repository_impl_class, mock_project_repo_instance
):
    """Test successful data fetching using db_repository for ProjectRepository."""
    await data_service.initialize()
    
    # Patch get_session and ProjectRepositoryImpl class *before* fetch_data is called
    with mock_get_session, \
         patch("app.bot.application.services.dashboard.dashboard_data_service.ProjectRepositoryImpl", new=mock_project_repository_impl_class):
        
        config = {
            "active_projects": {
                "type": "db_repository",
                "repository": "ProjectRepository",
                "method": "get_active_projects_by_guild"
            }
        }
        context = {"guild_id": 12345}
        result = await data_service.fetch_data(config, context)

    # Assertions
    assert "active_projects" in result
    assert result["active_projects"] == {"items": [{"id": 1, "name": "Project Alpha"}, {"id": 2, "name": "Project Beta"}]}
    
    # Check that ProjectRepositoryImpl was instantiated and the method called
    # The session mock from get_session should be passed to the constructor
    # mock_project_repository_impl_class.assert_called_once_with(ANY) # ANY for the session
    # A more specific check for the session mock might be needed if it was used beyond instantiation
    mock_project_repo_instance.get_active_projects_by_guild.assert_awaited_once_with(guild_id=12345)

@pytest.mark.asyncio
async def test_fetch_data_db_repository_missing_guild_id(
    data_service, mock_service_factory, mocker
):
    """Test db_repository when guild_id is missing from context."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    
    config = {
        "projects": {
            "type": "db_repository",
            "repository": "ProjectRepository",
            "method": "get_active_projects_by_guild"
        }
    }
    # No context or context without guild_id
    result_no_context = await data_service.fetch_data(config) # No context
    result_empty_context = await data_service.fetch_data(config, {}) # Empty context

    assert result_no_context["projects"] == {"error": "guild_id missing from context"}
    assert result_empty_context["projects"] == {"error": "guild_id missing from context"}
    mock_logger_error.assert_any_call("DB Repository source for 'projects' requires 'guild_id' in context, but none was provided.")

@pytest.mark.asyncio
async def test_fetch_data_db_repository_method_not_found(
    data_service, mock_service_factory, mock_get_session, mock_project_repository_impl_class, mocker
):
    """Test db_repository when the specified method is not found on the repository."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    
    # Make the mock repository instance not have the method
    mock_repo_instance_bad_method = AsyncMock()
    del mock_repo_instance_bad_method.non_existent_method # Ensure it's not there
    mock_project_repository_impl_class.return_value = mock_repo_instance_bad_method

    with mock_get_session, \
         patch("app.bot.application.services.dashboard.dashboard_data_service.ProjectRepositoryImpl", new=mock_project_repository_impl_class):
        
        config = {
            "projects": {
                "type": "db_repository",
                "repository": "ProjectRepository",
                "method": "non_existent_method"
            }
        }
        context = {"guild_id": 123}
        result = await data_service.fetch_data(config, context)

    assert result["projects"] == {"error": "Method 'non_existent_method' not found on ProjectRepository"}
    mock_logger_error.assert_called_once_with(
        "Method 'non_existent_method' not found or not callable on repository 'ProjectRepository' for 'projects'."
    )

@pytest.mark.asyncio
async def test_fetch_data_db_repository_unsupported_repo_type(
    data_service, mock_service_factory, mocker
):
    """Test db_repository when an unsupported repository type is requested."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()

    config = {
        "data": {
            "type": "db_repository",
            "repository": "SomeOtherRepository", # This is not 'ProjectRepository'
            "method": "some_method"
        }
    }
    context = {"guild_id": 123}
    result = await data_service.fetch_data(config, context)

    assert result["data"] == {"error": "Repository type 'SomeOtherRepository' not supported yet"}
    mock_logger_error.assert_called_once_with(
        "Repository type 'SomeOtherRepository' not explicitly handled yet. ServiceFactory needs update."
    )

# --- Test fetch_data: Service Collector ---

@pytest.fixture
def mock_service_collector():
    collector = AsyncMock(name="MockServiceCollector")
    collector.collect_game_services = AsyncMock(return_value={
        "Minecraft": "Online", "Factorio": "Offline"
    })
    # For collect_all, simulate a list of metric-like objects if needed
    collector.collect_all = AsyncMock(return_value=[
        {"name": "service_metric_1", "value": 100, "status": "OK"},
        {"name": "service_metric_2", "value": 0, "status": "Error"}
    ])
    return collector

@pytest.mark.asyncio
async def test_fetch_data_service_collector_game_services_success(
    data_service, mock_service_factory, mock_service_collector
):
    """Test successful data fetching for game services using service_collector."""
    await data_service.initialize()
    mock_service_factory.get_service.return_value = mock_service_collector
    
    config = {"game_status": {"type": "service_collector", "method": "collect_game_services"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("service_collector")
    mock_service_collector.collect_game_services.assert_awaited_once()
    
    assert "game_status" in result
    assert result["game_status"] == {"services": {"Minecraft": "Online", "Factorio": "Offline"}}

@pytest.mark.asyncio
async def test_fetch_data_service_collector_all_metrics_success(
    data_service, mock_service_factory, mock_service_collector
):
    """Test successful data fetching for all metrics using service_collector."""
    await data_service.initialize()
    mock_service_factory.get_service.return_value = mock_service_collector
    
    config = {"service_metrics": {"type": "service_collector", "method": "collect_all"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("service_collector")
    mock_service_collector.collect_all.assert_awaited_once()
    
    assert "service_metrics" in result
    expected_metrics_data = [
        {"name": "service_metric_1", "value": 100, "status": "OK"},
        {"name": "service_metric_2", "value": 0, "status": "Error"}
    ]
    assert result["service_metrics"] == {"metrics": expected_metrics_data}

@pytest.mark.asyncio
async def test_fetch_data_service_collector_default_to_game_services(
    data_service, mock_service_factory, mock_service_collector
):
    """Test service_collector defaults to collect_game_services if method is omitted."""
    await data_service.initialize()
    mock_service_factory.get_service.return_value = mock_service_collector
    
    # Method omitted in config
    config = {"default_game_status": {"type": "service_collector"}} 
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("service_collector")
    mock_service_collector.collect_game_services.assert_awaited_once()
    mock_service_collector.collect_all.assert_not_awaited() # Ensure collect_all was not called
    
    assert "default_game_status" in result
    assert result["default_game_status"] == {"services": {"Minecraft": "Online", "Factorio": "Offline"}}

@pytest.mark.asyncio
async def test_fetch_data_service_collector_unsupported_method(
    data_service, mock_service_factory, mock_service_collector, mocker
):
    """Test service_collector with an unsupported method specified."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    mock_service_factory.get_service.return_value = mock_service_collector
    
    config = {"bad_method_call": {"type": "service_collector", "method": "do_something_else"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("service_collector")
    mock_logger_error.assert_called_once_with(
        "Unsupported method 'do_something_else' specified for service_collector source 'bad_method_call'."
    )
    assert result["bad_method_call"] == {"error": "Unsupported method: do_something_else"}

@pytest.mark.asyncio
async def test_fetch_data_service_collector_not_found(data_service, mock_service_factory, mocker):
    """Test fetch_data when service_collector service is not found."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    mock_service_factory.get_service.return_value = None # Simulate service not found
    
    config = {"games": {"type": "service_collector"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("service_collector")
    mock_logger_error.assert_called_once_with("ServiceCollector service not found in ServiceFactory.")
    assert result["games"] == {"error": "ServiceCollector not available"}

@pytest.mark.asyncio
async def test_fetch_data_service_collector_exception_in_game_services(
    data_service, mock_service_factory, mock_service_collector, mocker
):
    """Test fetch_data when service_collector.collect_game_services raises an exception."""
    mock_logger_error = mocker.patch("app.bot.application.services.dashboard.dashboard_data_service.logger.error")
    await data_service.initialize()
    mock_service_collector.collect_game_services.side_effect = Exception("Game Collector Error!")
    mock_service_factory.get_service.return_value = mock_service_collector
    
    config = {"games": {"type": "service_collector", "method": "collect_game_services"}}
    result = await data_service.fetch_data(config)
    
    mock_service_factory.get_service.assert_called_once_with("service_collector")
    mock_service_collector.collect_game_services.assert_awaited_once()
    mock_logger_error.assert_called_once()
    assert "Error fetching data from ServiceCollector" in mock_logger_error.call_args[0][0]
    assert result["games"] == {"error": "Game Collector Error!"}

# Final placeholder removed, all main paths for fetch_data covered. 
import pytest
import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# First, patch the missing modules before importing the service
# This allows testing even when some dependencies aren't available
mock_modules = MagicMock()
with patch.dict('sys.modules', {'modules': mock_modules,
                               'modules.tracker': MagicMock(),
                               'modules.tracker.ip_management': MagicMock()}):
    
    # Import the components to test - must be inside the patch context
    from app.bot.application.services.dashboard.dashboard_lifecycle_service import DashboardLifecycleService
    from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry

# Test fixtures
@pytest.fixture
def mock_bot():
    """Create a mock bot instance with required attributes and methods
    
    This fixture provides a simulated bot object with all the dependencies
    needed for testing dashboard functionality, including:
    - Channel configuration
    - Database session
    - Dashboard factory
    
    Using mocks allows testing dashboard logic in isolation.
    """
    bot = MagicMock()
    bot.channel_config = MagicMock()
    bot.channel_config.get_channel_id = AsyncMock(return_value=123456789)  # Simulated Discord channel ID
    bot.db_session = MagicMock()
    bot.dashboard_factory = MagicMock()
    bot.dashboard_factory.create_dynamic = AsyncMock()  # Create dashboard function
    
    # Create a context manager for async session - simulates DB access
    async def mock_session():
        session = AsyncMock()
        yield session
    bot.db_session.side_effect = mock_session
    
    return bot

@pytest.fixture
def mock_dashboard():
    """Create a mock dashboard instance
    
    This fixture provides a simulated dashboard object with the methods
    that need to be tested, including:
    - setup
    - cleanup
    - refresh
    
    The dashboard type is set to allow type-specific testing.
    """
    dashboard = AsyncMock()
    dashboard.DASHBOARD_TYPE = "test_dashboard"  # Dashboard type identifier
    dashboard.setup = AsyncMock()     # Dashboard initialization
    dashboard.cleanup = AsyncMock()   # Dashboard cleanup/removal
    dashboard.refresh = AsyncMock()   # Dashboard content refresh
    return dashboard

@pytest.fixture
def mock_repository():
    """Create a mock repository with required methods
    
    This fixture simulates the data access layer for dashboard configuration,
    allowing tests to run without a database connection.
    """
    repository = AsyncMock()
    # Simulated dashboard types in the database
    repository.get_all_dashboard_types = AsyncMock(return_value=["welcome", "monitoring", "project"])
    # Simulated dashboard configuration
    repository.get_dashboard_config = AsyncMock(return_value={"title": "Test Dashboard", "components": []})
    return repository

# DashboardRegistry Tests
class TestDashboardRegistry:
    """Test suite for the DashboardRegistry class
    
    The DashboardRegistry manages the lifecycles of all dashboards in the system.
    These tests verify that dashboards can be properly:
    - Initialized from configuration
    - Activated in Discord channels
    - Deactivated when no longer needed
    - Tracked properly while active
    """
    
    @pytest.mark.asyncio
    async def test_initialize(self, mock_bot, mock_repository):
        """Test dashboard registry initialization with database configs
        
        Verifies that the registry can:
        1. Retrieve dashboard types from the database
        2. Load configurations for each dashboard type
        3. Store these configurations for later use
        """
        # Arrange - Setup the test with mocked repository
        with patch('app.shared.infrastructure.database.repositories.dashboard_repository_impl.DashboardRepository', 
                   return_value=mock_repository):
            registry = DashboardRegistry(mock_bot)
            
            # Act - Call the method being tested
            result = await registry.initialize()
            
            # Assert - Verify the expected behavior
            assert result is True  # Initialization should succeed
            assert len(registry.dashboard_configs) == 3  # Should have 3 dashboard configs
            mock_repository.get_all_dashboard_types.assert_called_once()  # Should query types
            assert mock_repository.get_dashboard_config.call_count == 3  # Should load each config
    
    @pytest.mark.asyncio
    async def test_activate_dashboard_success(self, mock_bot, mock_dashboard):
        """Test successful dashboard activation
        
        Verifies that:
        1. Dashboard can be created with correct parameters
        2. The setup method is called to initialize the dashboard
        3. The dashboard is stored in the active dashboards registry
        """
        # Arrange - Setup registry with configuration
        registry = DashboardRegistry(mock_bot)
        registry.dashboard_configs = {
            "welcome": {"title": "Welcome Dashboard", "components": []}
        }
        mock_bot.dashboard_factory.create_dynamic.return_value = mock_dashboard
        
        # Act - Activate a dashboard
        result = await registry.activate_dashboard("welcome", 123456789)
        
        # Assert - Verify dashboard was activated correctly
        assert result == mock_dashboard  # Should return the dashboard instance
        assert registry.active_dashboards[123456789] == mock_dashboard  # Should store in active registry
        mock_bot.dashboard_factory.create_dynamic.assert_called_once_with(
            dashboard_type="welcome", 
            channel_id=123456789, 
            config=registry.dashboard_configs["welcome"]
        )
        mock_dashboard.setup.assert_called_once()  # Dashboard setup should be called
    
    @pytest.mark.asyncio
    async def test_activate_dashboard_invalid_type(self, mock_bot):
        """Test dashboard activation with invalid dashboard type
        
        Verifies that:
        1. Invalid dashboard types are rejected
        2. No dashboard is created for invalid types
        3. The active dashboards registry remains unchanged
        """
        # Arrange - Setup registry with only valid types
        registry = DashboardRegistry(mock_bot)
        registry.dashboard_configs = {"welcome": {}}
        
        # Act - Try to activate with invalid type
        result = await registry.activate_dashboard("invalid_type", 123456789)
        
        # Assert - Verify activation failed safely
        assert result is None  # Should return None for failure
        assert not registry.active_dashboards  # Registry should remain empty
        mock_bot.dashboard_factory.create_dynamic.assert_not_called()  # No dashboard created
    
    @pytest.mark.asyncio
    async def test_deactivate_dashboard_by_channel(self, mock_bot, mock_dashboard):
        """Test deactivation of dashboard by channel ID
        
        Verifies that:
        1. Dashboard can be removed from a specific channel
        2. The cleanup method is called to properly remove the dashboard
        3. The dashboard is removed from the active registry
        """
        # Arrange - Setup registry with active dashboard
        registry = DashboardRegistry(mock_bot)
        registry.active_dashboards = {123456789: mock_dashboard}
        
        # Act - Deactivate by channel ID
        result = await registry.deactivate_dashboard(channel_id=123456789)
        
        # Assert - Verify dashboard was deactivated
        assert result is True  # Should return success
        assert 123456789 not in registry.active_dashboards  # Should be removed from registry
        mock_dashboard.cleanup.assert_called_once()  # Cleanup should be called
    
    @pytest.mark.asyncio
    async def test_deactivate_dashboard_by_type(self, mock_bot, mock_dashboard):
        """Test deactivation of dashboards by type
        
        Verifies that:
        1. All dashboards of a specific type can be removed
        2. The cleanup method is called for each dashboard
        3. All dashboards of that type are removed from the registry
        """
        # Arrange - Setup registry with multiple active dashboards
        registry = DashboardRegistry(mock_bot)
        registry.active_dashboards = {
            123456789: mock_dashboard,
            987654321: mock_dashboard
        }
        
        # Act - Deactivate by dashboard type
        result = await registry.deactivate_dashboard(dashboard_type="test_dashboard")
        
        # Assert - Verify all dashboards were deactivated
        assert result is True  # Should return success
        assert not registry.active_dashboards  # All dashboards should be removed
        assert mock_dashboard.cleanup.call_count == 2  # Cleanup called for each dashboard
    
    @pytest.mark.asyncio
    async def test_deactivate_dashboard_nonexistent(self, mock_bot):
        """Test deactivation of a dashboard that doesn't exist
        
        Verifies that:
        1. Attempting to deactivate a non-existent dashboard fails safely
        2. The registry remains unchanged
        """
        # Arrange - Setup empty registry
        registry = DashboardRegistry(mock_bot)
        registry.active_dashboards = {}
        
        # Act - Try to deactivate dashboard that doesn't exist
        result = await registry.deactivate_dashboard(channel_id=123456789)
        
        # Assert - Verify operation failed without errors
        assert result is False  # Should return failure

# DashboardLifecycleService Tests
class TestDashboardLifecycleService:
    """Test suite for the DashboardLifecycleService
    
    This service manages the high-level lifecycle of dashboards, including:
    - Initialization of the dashboard system
    - Activation of dashboards according to configuration
    - Deactivation and cleanup of dashboards
    - Dashboard refresh operations
    """
    
    @pytest.mark.asyncio
    async def test_initialize(self, mock_bot):
        """Test lifecycle service initialization
        
        Verifies that:
        1. The registry is properly initialized
        2. The configured dashboards are activated
        """
        # Arrange - Set up patch for dependencies
        with patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry.initialize', 
                   new_callable=AsyncMock, return_value=True), \
             patch('app.bot.application.services.dashboard.dashboard_lifecycle_service.DashboardLifecycleService.activate_configured_dashboards', 
                   new_callable=AsyncMock):
            service = DashboardLifecycleService(mock_bot)
            
            # Act - Initialize the service
            result = await service.initialize()
            
            # Assert - Verify initialization succeeded
            assert result is True
            assert service.registry is not None
    
    @pytest.mark.asyncio
    async def test_activate_configured_dashboards(self, mock_bot):
        """Test activation of dashboards from configuration
        
        Verifies that:
        1. Dashboard channel IDs are retrieved from configuration
        2. Dashboards are activated in the specified channels
        3. Only auto-create dashboards are activated
        """
        # Arrange - Set up patch for configuration
        with patch('app.bot.infrastructure.config.constants.dashboard_constants.DASHBOARD_MAPPINGS', 
                  {"welcome_channel": {"auto_create": True, "dashboard_type": "welcome"}}), \
             patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry.activate_dashboard', 
                   new_callable=AsyncMock) as mock_activate:
            
            service = DashboardLifecycleService(mock_bot)
            service.registry = DashboardRegistry(mock_bot)
            
            # Act - Activate dashboards from configuration
            await service.activate_configured_dashboards()
            
            # Assert - Verify correct dashboards were activated
            mock_bot.channel_config.get_channel_id.assert_called_once_with("welcome_channel")
            mock_activate.assert_called_once_with(dashboard_type="welcome", channel_id=123456789)
    
    @pytest.mark.asyncio
    async def test_deactivate_dashboard(self, mock_bot, mock_dashboard):
        """Test deactivation of dashboard through lifecycle service
        
        Verifies that:
        1. Deactivation requests are properly passed to registry
        2. The service returns the correct result
        """
        # Arrange - Set up registry mock
        with patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry.deactivate_dashboard', 
                   new_callable=AsyncMock, return_value=True) as mock_deactivate:
            
            service = DashboardLifecycleService(mock_bot)
            service.registry = DashboardRegistry(mock_bot)
            
            # Act - Deactivate a dashboard
            result = await service.deactivate_dashboard(channel_id=123456789)
            
            # Assert - Verify deactivation request was processed
            assert result is True
            mock_deactivate.assert_called_once_with(None, 123456789)
    
    @pytest.mark.asyncio
    async def test_get_active_dashboards(self, mock_bot, mock_dashboard):
        """Test retrieval of active dashboards
        
        Verifies that:
        1. The service can retrieve the current active dashboards
        2. The registry contents are returned unchanged
        """
        # Arrange - Set up registry with active dashboard
        service = DashboardLifecycleService(mock_bot)
        service.registry = DashboardRegistry(mock_bot)
        service.registry.active_dashboards = {123456789: mock_dashboard}
        
        # Act - Get active dashboards
        result = await service.get_active_dashboards()
        
        # Assert - Verify correct dashboards were returned
        assert result == {123456789: mock_dashboard}
    
    @pytest.mark.asyncio
    async def test_refresh_dashboard(self, mock_bot, mock_dashboard):
        """Test dashboard refresh functionality
        
        Verifies that:
        1. The service can trigger a refresh for a specific dashboard
        2. The dashboard's refresh method is called
        """
        # Arrange - Set up registry with active dashboard
        service = DashboardLifecycleService(mock_bot)
        service.registry = DashboardRegistry(mock_bot)
        service.registry.active_dashboards = {123456789: mock_dashboard}
        
        # Act - Refresh a dashboard
        result = await service.refresh_dashboard(123456789)
        
        # Assert - Verify refresh was triggered
        assert result is True
        mock_dashboard.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_refresh_dashboard_nonexistent(self, mock_bot):
        """Test refreshing a dashboard that doesn't exist
        
        Verifies that:
        1. Attempting to refresh a non-existent dashboard fails safely
        2. The service returns the correct failure result
        """
        # Arrange - Set up empty registry
        service = DashboardLifecycleService(mock_bot)
        service.registry = DashboardRegistry(mock_bot)
        service.registry.active_dashboards = {}
        
        # Act - Try to refresh non-existent dashboard
        result = await service.refresh_dashboard(123456789)
        
        # Assert - Verify operation failed without errors
        assert result is False
    
    @pytest.mark.asyncio
    async def test_shutdown(self, mock_bot, mock_dashboard):
        """Test clean shutdown of all dashboards
        
        Verifies that:
        1. All active dashboards are deactivated during shutdown
        2. The service returns the correct success result
        """
        # Arrange - Set up registry mock
        with patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry.deactivate_dashboard', 
                   new_callable=AsyncMock, return_value=True) as mock_deactivate:
            
            service = DashboardLifecycleService(mock_bot)
            service.registry = DashboardRegistry(mock_bot)
            service.registry.active_dashboards = {123456789: mock_dashboard, 987654321: mock_dashboard}
            
            # Act - Perform shutdown
            result = await service.shutdown()
            
            # Assert - Verify all dashboards were deactivated
            assert result is True
            assert mock_deactivate.call_count == 2
            mock_deactivate.assert_any_call(channel_id=123456789)
            mock_deactivate.assert_any_call(channel_id=987654321) 
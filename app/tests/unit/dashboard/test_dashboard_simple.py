import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# We need to patch the modules import before importing DashboardLifecycleService
# This is necessary because the tests need to run even if some dependencies are missing
mock_modules = MagicMock()
with patch.dict('sys.modules', {'modules': mock_modules, 
                               'modules.tracker': MagicMock(),
                               'modules.tracker.ip_management': MagicMock()}):
    
    # Now we can safely import our service
    from app.bot.application.services.dashboard.dashboard_lifecycle_service import DashboardLifecycleService
    from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry

# Test fixtures
@pytest.fixture
def mock_bot():
    """Create a mock bot instance with required attributes and methods
    
    This fixture provides a minimal bot object with just enough attributes
    to test dashboard functionality without other dependencies.
    """
    bot = MagicMock()
    bot.channel_config = MagicMock()
    bot.channel_config.get_channel_id = AsyncMock(return_value=123456789)  # Discord channel ID
    bot.db_session = MagicMock()  # Database session manager
    bot.dashboard_factory = MagicMock()  # Creates dashboard instances
    bot.dashboard_factory.create_dynamic = AsyncMock()
    
    # Create a context manager for async session
    async def mock_session():
        session = AsyncMock()
        yield session
    bot.db_session.side_effect = mock_session
    
    return bot

@pytest.fixture
def mock_dashboard():
    """Create a mock dashboard instance
    
    This fixture provides a simple dashboard object with the required
    methods for testing basic functionality.
    """
    dashboard = AsyncMock()
    dashboard.DASHBOARD_TYPE = "test_dashboard"  # Dashboard type
    dashboard.setup = AsyncMock()     # Initialize dashboard
    dashboard.cleanup = AsyncMock()   # Cleanup dashboard
    dashboard.refresh = AsyncMock()   # Update dashboard content
    return dashboard

# Simple Sanity Test
def test_service_can_be_instantiated(mock_bot):
    """Simple test to verify we can create the service
    
    This test ensures that the basic class structure and dependencies
    are set up correctly, allowing the service to be instantiated.
    """
    # This test will help verify our mocking approach works
    with patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry'):
        service = DashboardLifecycleService(mock_bot)
        assert service is not None
        assert service.bot == mock_bot

@pytest.mark.asyncio
async def test_simple_lifecycle(mock_bot, mock_dashboard):
    """Basic test of dashboard lifecycle
    
    This simplified test verifies the core functionality of the dashboard
    lifecycle service without the complexity of the full test suite.
    It focuses on initialization and refresh operations.
    """
    with patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry') as MockRegistry:
        # Setup mocks
        registry_instance = MockRegistry.return_value
        registry_instance.initialize = AsyncMock(return_value=True)
        registry_instance.active_dashboards = {123456789: mock_dashboard}
        
        # Create service with our mocked dependencies
        service = DashboardLifecycleService(mock_bot)
        
        # Call initialize
        with patch.object(service, 'activate_configured_dashboards', AsyncMock()):
            result = await service.initialize()
            assert result is True
        
        # Test refresh functionality
        registry_instance.active_dashboards = {123456789: mock_dashboard}
        result = await service.refresh_dashboard(123456789)
        assert result is True
        mock_dashboard.refresh.assert_called_once() 
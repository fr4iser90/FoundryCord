import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Import the components to test
from app.bot.application.services.dashboard.dashboard_lifecycle_service import DashboardLifecycleService
from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry

# Test fixtures
@pytest.fixture
def mock_bot():
    """Create a mock bot instance with required attributes and methods"""
    bot = MagicMock()
    bot.channel_config = MagicMock()
    bot.channel_config.get_channel_id = AsyncMock(return_value=123456789)
    bot.db_session = MagicMock()
    bot.dashboard_factory = MagicMock()
    bot.dashboard_factory.create_dynamic = AsyncMock()
    
    # Create a context manager for async session
    async def mock_session():
        session = AsyncMock()
        yield session
    bot.db_session.side_effect = mock_session
    
    return bot

@pytest.fixture
def mock_dashboard():
    """Create a mock dashboard instance"""
    dashboard = AsyncMock()
    dashboard.DASHBOARD_TYPE = "test_dashboard"
    dashboard.setup = AsyncMock()
    dashboard.cleanup = AsyncMock()
    dashboard.refresh = AsyncMock()
    return dashboard

@pytest.fixture
def mock_repository():
    """Create a mock repository with required methods"""
    repository = AsyncMock()
    repository.get_all_dashboard_types = AsyncMock(return_value=["welcome", "monitoring", "project"])
    repository.get_dashboard_config = AsyncMock(return_value={"title": "Test Dashboard", "components": []})
    return repository

# DashboardLifecycleService Tests
class TestDashboardLifecycleService:
    
    @pytest.mark.asyncio
    async def test_initialize(self, mock_bot):
        """Test lifecycle service initialization"""
        # Arrange
        with patch('app.bot.infrastructure.dashboards.dashboard_registry.DashboardRegistry.initialize', 
                   new_callable=AsyncMock, return_value=True), \
             patch('app.bot.application.services.dashboard.dashboard_lifecycle_service.DashboardLifecycleService.activate_configured_dashboards', 
                   new_callable=AsyncMock):
            service = DashboardLifecycleService(mock_bot)
            
            # Act
            result = await service.initialize()
            
            # Assert
            assert result is True
            assert service.registry is not None 
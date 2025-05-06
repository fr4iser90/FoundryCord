import pytest
from unittest.mock import MagicMock, Mock, call
from app.bot.infrastructure.factories.service_factory import ServiceFactory

# --- Fixtures ---

@pytest.fixture
def mock_bot():
    """Provides a mock bot instance."""
    return MagicMock()

@pytest.fixture
def service_factory(mock_bot):
    """Provides a ServiceFactory instance initialized with a mock bot."""
    return ServiceFactory(bot=mock_bot)

@pytest.fixture
def sample_service_instance():
    """Provides a simple mock service instance."""
    return Mock(name="SampleServiceInstance")

@pytest.fixture
def sample_service_creator(sample_service_instance):
    """Provides a simple mock service creator function."""
    # Creator should ideally return a new mock each time if needed,
    # but for basic registration tests, returning the same mock is fine.
    creator = Mock(name="SampleServiceCreator", return_value=sample_service_instance)
    return creator

# --- Test Cases ---

def test_initialization(service_factory, mock_bot):
    """Test that the factory initializes correctly."""
    assert service_factory.bot is mock_bot
    assert service_factory._services == {}
    assert service_factory._creators == {}

# --- Test register_service ---

def test_register_service_new(service_factory, sample_service_instance):
    """Test registering a new service instance."""
    service_factory.register_service("service1", sample_service_instance)
    assert "service1" in service_factory._services
    assert service_factory._services["service1"] is sample_service_instance

def test_register_service_overwrite_false(service_factory, sample_service_instance, mocker):
    """Test registering a service when it exists and overwrite is False (default)."""
    mock_logger_warning = mocker.patch("app.bot.infrastructure.factories.service_factory.logger.warning")
    service_factory.register_service("service1", sample_service_instance) # Initial registration
    
    new_instance = Mock(name="NewInstance")
    service_factory.register_service("service1", new_instance) # Attempt to register again
    
    assert service_factory._services["service1"] is sample_service_instance # Should still be the original
    mock_logger_warning.assert_called_once()
    assert "already registered" in mock_logger_warning.call_args[0][0]

def test_register_service_overwrite_true(service_factory, sample_service_instance):
    """Test registering a service when it exists and overwrite is True."""
    service_factory.register_service("service1", sample_service_instance) # Initial registration
    
    new_instance = Mock(name="NewInstance")
    service_factory.register_service("service1", new_instance, overwrite=True) # Register again with overwrite
    
    assert service_factory._services["service1"] is new_instance # Should be the new instance

# --- Test register_service_creator ---

def test_register_service_creator_new(service_factory, sample_service_creator):
    """Test registering a new service creator."""
    service_factory.register_service_creator("creator1", sample_service_creator)
    assert "creator1" in service_factory._creators
    assert service_factory._creators["creator1"] is sample_service_creator

def test_register_service_creator_overwrite_false(service_factory, sample_service_creator, mocker):
    """Test registering a creator when it exists and overwrite is False (default)."""
    mock_logger_warning = mocker.patch("app.bot.infrastructure.factories.service_factory.logger.warning")
    service_factory.register_service_creator("creator1", sample_service_creator) # Initial registration
    
    new_creator = Mock(name="NewCreator")
    service_factory.register_service_creator("creator1", new_creator) # Attempt to register again
    
    assert service_factory._creators["creator1"] is sample_service_creator # Should still be the original
    mock_logger_warning.assert_called_once()
    assert "already registered" in mock_logger_warning.call_args[0][0]

def test_register_service_creator_overwrite_true(service_factory, sample_service_creator):
    """Test registering a creator when it exists and overwrite is True."""
    service_factory.register_service_creator("creator1", sample_service_creator) # Initial registration
    
    new_creator = Mock(name="NewCreator")
    service_factory.register_service_creator("creator1", new_creator, overwrite=True) # Register again with overwrite
    
    assert service_factory._creators["creator1"] is new_creator # Should be the new creator

# --- Test get_service ---

def test_get_service_existing_instance(service_factory, sample_service_instance):
    """Test getting a service that's already registered as an instance."""
    service_factory.register_service("service1", sample_service_instance)
    retrieved_service = service_factory.get_service("service1")
    assert retrieved_service is sample_service_instance

def test_get_service_via_creator(service_factory, sample_service_creator, sample_service_instance, mock_bot):
    """Test getting a service that needs to be created via a registered creator."""
    service_factory.register_service_creator("creator1", sample_service_creator)
    
    # Ensure it's not in the instance cache initially
    assert "creator1" not in service_factory._services
    
    retrieved_service = service_factory.get_service("creator1")
    
    # Check that the creator was called with the bot
    sample_service_creator.assert_called_once_with(mock_bot)
    # Check that the correct instance was returned
    assert retrieved_service is sample_service_instance
    # Check that the instance is now cached
    assert "creator1" in service_factory._services
    assert service_factory._services["creator1"] is sample_service_instance

def test_get_service_via_creator_only_once(service_factory, sample_service_creator, sample_service_instance, mock_bot):
    """Test that the creator is only called once, and subsequent gets use the cache."""
    service_factory.register_service_creator("creator1", sample_service_creator)
    
    # First get - should call creator
    service1 = service_factory.get_service("creator1")
    sample_service_creator.assert_called_once_with(mock_bot)
    assert service1 is sample_service_instance
    
    # Second get - should use cache, not call creator again
    service2 = service_factory.get_service("creator1")
    sample_service_creator.assert_called_once() # Still only called once
    assert service2 is sample_service_instance

def test_get_service_creator_returns_none(service_factory, mock_bot, mocker):
    """Test getting a service when the creator returns None."""
    mock_logger_error = mocker.patch("app.bot.infrastructure.factories.service_factory.logger.error")
    failing_creator = Mock(name="FailingCreator", return_value=None)
    service_factory.register_service_creator("fails", failing_creator)
    
    retrieved_service = service_factory.get_service("fails")
    
    assert retrieved_service is None
    failing_creator.assert_called_once_with(mock_bot)
    mock_logger_error.assert_called_once()
    assert "returned None" in mock_logger_error.call_args[0][0]

def test_get_service_creator_raises_exception(service_factory, mock_bot, mocker):
    """Test getting a service when the creator raises an exception."""
    mock_logger_error = mocker.patch("app.bot.infrastructure.factories.service_factory.logger.error")
    exception_creator = Mock(name="ExceptionCreator", side_effect=ValueError("Creation failed"))
    service_factory.register_service_creator("raises_ex", exception_creator)
    
    retrieved_service = service_factory.get_service("raises_ex")
    
    assert retrieved_service is None
    exception_creator.assert_called_once_with(mock_bot)
    mock_logger_error.assert_called_once()
    assert "Error creating service" in mock_logger_error.call_args[0][0]
    assert "Creation failed" in mock_logger_error.call_args[0][0]

def test_get_service_not_found(service_factory, mocker):
    """Test getting a service that is not registered at all."""
    mock_logger_error = mocker.patch("app.bot.infrastructure.factories.service_factory.logger.error")
    retrieved_service = service_factory.get_service("nonexistent")
    assert retrieved_service is None
    mock_logger_error.assert_called_once()
    assert "not found. No instance registered and no creator available" in mock_logger_error.call_args[0][0]

# --- Test has_service ---

def test_has_service_instance_registered(service_factory, sample_service_instance):
    """Test has_service when an instance is registered."""
    service_factory.register_service("service1", sample_service_instance)
    assert service_factory.has_service("service1") is True

def test_has_service_creator_registered(service_factory, sample_service_creator):
    """Test has_service when only a creator is registered."""
    service_factory.register_service_creator("creator1", sample_service_creator)
    assert service_factory.has_service("creator1") is True

def test_has_service_not_registered(service_factory):
    """Test has_service when the service is not registered."""
    assert service_factory.has_service("nonexistent") is False

# --- Test get_all_services ---

def test_get_all_services_empty(service_factory):
    """Test get_all_services when no instances are registered (only creators might exist)."""
    service_factory.register_service_creator("creator1", Mock())
    all_services = service_factory.get_all_services()
    assert isinstance(all_services, dict)
    assert len(all_services) == 0 # Should only return cached instances

def test_get_all_services_with_instances(service_factory, sample_service_instance):
    """Test get_all_services when instances are registered."""
    instance1 = sample_service_instance
    instance2 = Mock(name="OtherService")
    service_factory.register_service("service1", instance1)
    service_factory.register_service("service2", instance2)
    service_factory.register_service_creator("creator1", Mock()) # Should not be included
    
    all_services = service_factory.get_all_services()
    
    assert isinstance(all_services, dict)
    assert len(all_services) == 2
    assert all_services["service1"] is instance1
    assert all_services["service2"] is instance2
    assert "creator1" not in all_services

def test_get_all_services_includes_created_via_creator(service_factory, sample_service_creator):
    """Test that get_all_services includes services created via creator."""
    service_factory.register_service_creator("creator1", sample_service_creator)
    service_factory.get_service("creator1") # Trigger creation and caching
    
    all_services = service_factory.get_all_services()
    assert len(all_services) == 1
    assert "creator1" in all_services
    assert all_services["creator1"] is sample_service_creator.return_value

def test_get_all_services_returns_copy(service_factory, sample_service_instance):
    """Test that get_all_services returns a copy, not the internal dict."""
    service_factory.register_service("service1", sample_service_instance)
    all_services = service_factory.get_all_services()
    all_services["new_key"] = "new_value" # Modify the returned dict
    
    # Check that the internal dict was not modified
    assert "new_key" not in service_factory._services
    assert service_factory.get_all_services() == {"service1": sample_service_instance} 
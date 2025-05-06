import pytest
from unittest.mock import MagicMock, Mock, AsyncMock, patch, call
from app.bot.infrastructure.factories.component_factory import ComponentFactory
# Assuming ComponentDefinition is accessible for mocking structure, or use MagicMock
# If ComponentDefinition is complex, might need to define a mock structure
# from app.bot.infrastructure.config.registries.component_registry import ComponentDefinition

# --- Fixtures ---

@pytest.fixture
def mock_registry():
    """Provides a mock ComponentRegistryInterface."""
    registry = MagicMock(name="MockComponentRegistry")
    # Mock the methods used by the factory
    registry.get_component_definition = MagicMock(name="get_component_definition")
    return registry

@pytest.fixture
def component_factory(mock_registry):
    """Provides a ComponentFactory instance initialized with a mock registry."""
    return ComponentFactory(component_registry=mock_registry)

@pytest.fixture
def mock_component_class():
    """Provides a mock component class."""
    # Use AsyncMock if the component's __init__ is async, otherwise Mock
    component_class = Mock(name="MockComponentClass") 
    # Mock the instance returned by the class constructor
    component_instance = Mock(name="MockComponentInstance")
    component_class.return_value = component_instance
    return component_class

@pytest.fixture
def mock_component_definition(mock_component_class):
    """Provides a mock component definition object."""
    # Simulate the structure returned by registry.get_component_definition
    definition = Mock(name="MockComponentDefinition")
    definition.component_class = mock_component_class
    definition.default_config = {"color": "blue", "size": 10}
    return definition

# --- Test Cases for create_component ---

@pytest.mark.asyncio
async def test_create_component_success(component_factory, mock_registry, mock_component_definition, mock_component_class):
    """Test successful creation of a component."""
    mock_registry.get_component_definition.return_value = mock_component_definition
    
    component_type = "test_type"
    component_id = "test_id_123"
    instance_config = {"size": 12, "label": "Test"}
    
    created_component = await component_factory.create_component(
        component_type, component_id, instance_config
    )
    
    # Verify registry was called
    mock_registry.get_component_definition.assert_called_once_with(component_type)
    
    # Verify component class was instantiated with merged config
    expected_merged_config = {"color": "blue", "size": 12, "label": "Test"}
    mock_component_class.assert_called_once_with(
        component_id=component_id,
        config=expected_merged_config
    )
    
    # Verify the created instance is returned
    assert created_component is mock_component_class.return_value

@pytest.mark.asyncio
async def test_create_component_type_not_found(component_factory, mock_registry, mocker):
    """Test component creation when the component type is not registered."""
    mock_logger_error = mocker.patch("app.bot.infrastructure.factories.component_factory.logger.error")
    mock_registry.get_component_definition.return_value = None # Simulate type not found
    
    created_component = await component_factory.create_component(
        "unknown_type", "test_id_456", {}
    )
    
    # Verify registry was called
    mock_registry.get_component_definition.assert_called_once_with("unknown_type")
    
    # Verify None is returned and error is logged
    assert created_component is None
    mock_logger_error.assert_called_once()
    assert "type 'unknown_type' not registered" in mock_logger_error.call_args[0][0]

@pytest.mark.asyncio
async def test_create_component_instantiation_error(component_factory, mock_registry, mock_component_definition, mock_component_class, mocker):
    """Test component creation when the component class instantiation fails."""
    mock_logger_error = mocker.patch("app.bot.infrastructure.factories.component_factory.logger.error")
    mock_registry.get_component_definition.return_value = mock_component_definition
    
    # Simulate an error during component instantiation
    error_message = "Instantiation failed!"
    mock_component_class.side_effect = ValueError(error_message) 
    
    component_type = "error_type"
    component_id = "error_id_789"
    
    created_component = await component_factory.create_component(
        component_type, component_id, {}
    )
    
    # Verify registry was called
    mock_registry.get_component_definition.assert_called_once_with(component_type)
    
    # Verify instantiation was attempted
    expected_merged_config = mock_component_definition.default_config # Merged with empty dict
    mock_component_class.assert_called_once_with(
        component_id=component_id,
        config=expected_merged_config
    )

    # Verify None is returned and error is logged
    assert created_component is None
    mock_logger_error.assert_called_once()
    assert f"Error creating component '{component_id}'" in mock_logger_error.call_args[0][0]
    assert error_message in mock_logger_error.call_args[0][0]

# --- Test Cases for create (Facade Method) ---
# We can add basic tests to ensure 'create' calls the correct underlying method

@pytest.mark.asyncio
async def test_create_facade_calls_create_component(component_factory, mocker):
    """Test that the create facade calls create_component for non-dashboard types."""
    # Mock the actual create_component method within the factory instance
    component_factory.create_component = AsyncMock(name="create_component_mock")
    
    component_type = "button"
    kwargs = {"component_id": "btn1", "config": {"label": "Click"}}
    
    await component_factory.create(component_type, **kwargs)
    
    component_factory.create_component.assert_awaited_once_with(
        component_type, kwargs.get('component_id'), kwargs.get('config', {})
    )

@pytest.mark.asyncio
async def test_create_facade_calls_create_dashboard_controller(component_factory, mocker):
    """Test that the create facade calls create_dashboard_controller for type 'dashboard'."""
     # Mock the actual create_dashboard_controller method
    component_factory.create_dashboard_controller = AsyncMock(name="create_dashboard_controller_mock")
    
    component_type = "dashboard" # Special case type
    kwargs = {"dashboard_id": "dash1", "dashboard_type": "monitoring", "channel_id": 123}
    
    await component_factory.create(component_type, **kwargs)
    
    component_factory.create_dashboard_controller.assert_awaited_once_with(**kwargs)

# --- Test Cases for create_components_from_definitions ---

@pytest.mark.asyncio
async def test_create_components_from_definitions(component_factory):
    """Test creating multiple components from a list of definitions."""
    definitions_data = [
        {"id": "comp1", "type": "button", "config": {"label": "B1"}},
        {"id": "comp2", "type": "embed", "config": {"title": "E1"}},
        {"id": "invalid"}, # Missing type
        {"type": "selector", "config": {}}, # Missing id
    ]
    
    # Mock the underlying create_component to simulate success/failure
    async def mock_create_component(*, component_type, component_id, config, **kwargs):
        if component_type == "button" and component_id == "comp1":
            return Mock(name="ButtonInstance")
        if component_type == "embed" and component_id == "comp2":
            return Mock(name="EmbedInstance")
        return None # Simulate failure for others or if called unexpectedly

    component_factory.create_component = AsyncMock(side_effect=mock_create_component)
    
    created_components = await component_factory.create_components_from_definitions(definitions_data)
    
    # Check calls to create_component (ignoring invalid ones)
    expected_calls = [
        call(component_type="button", component_id="comp1", config={"label": "B1"}),
        call(component_type="embed", component_id="comp2", config={"title": "E1"}),
    ]
    component_factory.create_component.assert_has_awaits(expected_calls, any_order=True)
    assert component_factory.create_component.await_count == 2 # Only valid ones called
    
    # Check the returned dictionary
    assert len(created_components) == 2
    assert "comp1" in created_components
    assert "comp2" in created_components
    assert created_components["comp1"]._mock_name == "ButtonInstance"
    assert created_components["comp2"]._mock_name == "EmbedInstance"
    assert "invalid" not in created_components
    assert "selector" not in created_components # Assuming id was required 
"""Unit tests for ComponentRegistry."""
import pytest
import pytest_asyncio
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Import the class to test
from app.bot.infrastructure.config.registries.component_registry import ComponentRegistry, ComponentDefinition
from app.bot.interfaces.dashboards.components.base_component import BaseComponent
from app.shared.infrastructure.models.dashboards import DashboardComponentDefinitionEntity
from app.shared.infrastructure.repositories.dashboards import DashboardComponentDefinitionRepositoryImpl

# --- Dummy Components for Testing ---

class MockEmbedComponent(BaseComponent):
    async def build(self, data: dict):
        return "Mock Embed Build"

class MockButtonComponent(BaseComponent):
     async def build(self, data: dict):
        return "Mock Button Build"

# --- Fixtures ---

@pytest.fixture
def registry():
    """Provides a fresh ComponentRegistry instance for each test."""
    return ComponentRegistry()

# --- Test Cases ---

def test_initialization(registry: ComponentRegistry):
    """Test that the registry initializes with empty dictionaries."""
    assert registry._components == {}
    assert registry._definitions_by_key == {}
    assert registry.bot is None
    assert not registry._db_definitions_loaded

def test_register_component_success(registry: ComponentRegistry):
    """Test successful registration of a component implementation class."""
    registry.register_component(
        component_type="embed",
        component_class=MockEmbedComponent,
        description="Test Embed",
        default_config={"color": "blue"}
    )
    
    assert "embed" in registry._components
    definition = registry._components["embed"]
    assert isinstance(definition, ComponentDefinition)
    assert definition.component_type == "embed"
    assert definition.component_class == MockEmbedComponent
    assert definition.description == "Test Embed"
    assert definition.default_config == {"color": "blue"}
    
    # Test registering another component
    registry.register_component("button", MockButtonComponent, "Test Button")
    assert "button" in registry._components
    assert registry._components["button"].component_class == MockButtonComponent
    assert registry._components["button"].default_config == {} # Test default empty dict

def test_register_component_overwrite(registry: ComponentRegistry, mocker):
    """Test that registering the same type overwrites the previous one (with a warning)."""
    mock_logger_warning = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.warning")
    
    registry.register_component("embed", MockEmbedComponent, "First Embed")
    registry.register_component("embed", MockButtonComponent, "Overwrite Embed") # Use different class

    assert "embed" in registry._components
    assert registry._components["embed"].component_class == MockButtonComponent # Overwritten
    assert registry._components["embed"].description == "Overwrite Embed"
    mock_logger_warning.assert_called_once_with("Component implementation class for type 'embed' already registered, overwriting.")

def test_get_component_class_success(registry: ComponentRegistry):
    """Test retrieving a registered component class."""
    registry.register_component("embed", MockEmbedComponent, "Test Embed")
    
    component_class = registry.get_component_class("embed")
    assert component_class == MockEmbedComponent

def test_get_component_class_not_registered(registry: ComponentRegistry, mocker):
    """Test retrieving a non-existent component class."""
    mock_logger_error = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.error")
    
    component_class = registry.get_component_class("nonexistent")
    assert component_class is None
    mock_logger_error.assert_called_once_with("Component implementation class for type 'nonexistent' not found in registry. Ensure it was registered.")

@pytest.mark.asyncio
async def test_initialize_loads_definitions_success(registry: ComponentRegistry, mocker):
    """Test successful loading of definitions from the mocked database."""
    # Mock DB entities
    mock_def_1 = DashboardComponentDefinitionEntity(
        id=1, component_key="embed_welcome", component_type="embed", dashboard_type="welcome",
        definition=json.dumps({"title": "Welcome!", "description": "..."})
    )
    mock_def_2 = DashboardComponentDefinitionEntity(
        id=2, component_key="button_refresh", component_type="button", dashboard_type="*", # Test different dashboard type
        definition={"label": "Refresh", "style": "primary"} # Test definition as dict
    )
    
    # Mock Repository
    mock_repo_instance = AsyncMock(spec=DashboardComponentDefinitionRepositoryImpl)
    mock_repo_instance.list_definitions.return_value = [mock_def_1, mock_def_2]
    
    MockDashboardComponentDefinitionRepositoryImpl = mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.DashboardComponentDefinitionRepositoryImpl",
        return_value=mock_repo_instance
    )
    
    # Mock session_context
    mock_session = AsyncMock()
    mock_session_context = mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.session_context",
        return_value=mock_session # Return the async context manager
    )
    mock_session.__aenter__.return_value = mock_session # Context manager returns the session

    # Mock bot object
    mock_bot = MagicMock()

    # --- Call the method ---
    success = await registry.initialize(mock_bot)
    # --- Assertions ---
    assert success is True
    assert registry.bot == mock_bot
    assert registry._db_definitions_loaded is True
    
    # Check repo was called correctly
    mock_session_context.assert_called_once()
    MockDashboardComponentDefinitionRepositoryImpl.assert_called_once_with(mock_session)
    mock_repo_instance.list_definitions.assert_awaited_once()
    
    # Check definitions were stored
    assert len(registry._definitions_by_key) == 2
    assert "embed_welcome" in registry._definitions_by_key
    assert "button_refresh" in registry._definitions_by_key
    
    assert registry._definitions_by_key["embed_welcome"] == {
        "type": "embed", "key": "embed_welcome", "dashboard_type": "welcome",
        "definition": {"title": "Welcome!", "description": "..."}
    }
    assert registry._definitions_by_key["button_refresh"] == {
        "type": "button", "key": "button_refresh", "dashboard_type": "*",
        "definition": {"label": "Refresh", "style": "primary"}
    }

@pytest.mark.asyncio
async def test_initialize_already_loaded(registry: ComponentRegistry, mocker):
    """Test that initialize doesn't reload if already loaded."""
    mock_session_context = mocker.patch("app.bot.infrastructure.config.registries.component_registry.session_context")
    mock_logger_debug = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.debug")
    
    registry._db_definitions_loaded = True # Mark as loaded
    mock_bot = MagicMock()
    
    success = await registry.initialize(mock_bot)
    
    assert success is True
    mock_session_context.assert_not_called() # DB should not be touched
    # Check for the specific debug message indicating it was already loaded
    mock_logger_debug.assert_any_call("Database component definitions already loaded.")


@pytest.mark.asyncio
async def test_initialize_handles_db_error(registry: ComponentRegistry, mocker):
    """Test that initialize returns False and logs error on DB repository failure."""
    mock_repo_instance = AsyncMock(spec=DashboardComponentDefinitionRepositoryImpl)
    mock_repo_instance.list_definitions.side_effect = Exception("DB Connection Failed")
    
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.DashboardComponentDefinitionRepositoryImpl",
        return_value=mock_repo_instance
    )
    mock_session = AsyncMock()
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.session_context",
        return_value=mock_session
    )
    mock_session.__aenter__.return_value = mock_session
    mock_logger_error = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.error")
    
    mock_bot = MagicMock()
    success = await registry.initialize(mock_bot)
    
    assert success is False
    assert registry._db_definitions_loaded is False # Should not be marked as loaded
    mock_logger_error.assert_called_once_with(
        "Failed to load component definitions from database: DB Connection Failed", exc_info=True
    )

@pytest.mark.asyncio
async def test_initialize_handles_json_error(registry: ComponentRegistry, mocker):
    """Test that initialize logs error and continues if one definition has bad JSON."""
    # Mock DB entities - one good, one bad
    mock_def_good = DashboardComponentDefinitionEntity(
        id=1, component_key="embed_good", component_type="embed", dashboard_type="welcome",
        definition=json.dumps({"title": "Good"})
    )
    mock_def_bad = DashboardComponentDefinitionEntity(
        id=2, component_key="button_bad_json", component_type="button", dashboard_type="*",
        definition="{not valid json" # Invalid JSON string
    )
    mock_def_invalid_format = DashboardComponentDefinitionEntity(
        id=3, component_key="invalid_format", component_type="other", dashboard_type="test",
        definition=123 # Invalid type
    )


    mock_repo_instance = AsyncMock(spec=DashboardComponentDefinitionRepositoryImpl)
    mock_repo_instance.list_definitions.return_value = [mock_def_good, mock_def_bad, mock_def_invalid_format]
    
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.DashboardComponentDefinitionRepositoryImpl",
        return_value=mock_repo_instance
    )
    mock_session = AsyncMock()
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.session_context",
        return_value=mock_session
    )
    mock_session.__aenter__.return_value = mock_session
    mock_logger_error = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.error")
    mock_logger_warning = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.warning")


    mock_bot = MagicMock()
    success = await registry.initialize(mock_bot)
    
    assert success is True # Should still succeed overall
    assert registry._db_definitions_loaded is True
    assert len(registry._definitions_by_key) == 1 # Only the good one loaded
    assert "embed_good" in registry._definitions_by_key
    assert "button_bad_json" not in registry._definitions_by_key
    assert "invalid_format" not in registry._definitions_by_key
    
    # Check that errors/warnings were logged for the bad ones
    mock_logger_error.assert_called_once_with(
        "Failed to parse JSON definition for component key 'button_bad_json': Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"
    )
    mock_logger_warning.assert_called_once_with(
         "Skipping definition for key 'invalid_format': Invalid format in DB - <class 'int'>"
    )

@pytest.mark.asyncio
async def test_get_definition_and_type_by_key(registry: ComponentRegistry, mocker):
    """Test get_definition_by_key and get_type_by_key after successful initialize."""
    # Use the successful initialize mock setup
    mock_def_1 = DashboardComponentDefinitionEntity(
        id=1, component_key="embed_welcome", component_type="embed", dashboard_type="welcome",
        definition=json.dumps({"title": "Welcome!"})
    )
    mock_repo_instance = AsyncMock(spec=DashboardComponentDefinitionRepositoryImpl)
    mock_repo_instance.list_definitions.return_value = [mock_def_1]
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.DashboardComponentDefinitionRepositoryImpl",
        return_value=mock_repo_instance
    )
    mock_session = AsyncMock()
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.session_context",
        return_value=mock_session
    )
    mock_session.__aenter__.return_value = mock_session
    mock_bot = MagicMock()
    await registry.initialize(mock_bot) # Load data first

    # --- Test get_definition_by_key ---
    definition = registry.get_definition_by_key("embed_welcome")
    assert definition is not None
    assert definition["key"] == "embed_welcome"
    assert definition["type"] == "embed"
    assert definition["definition"] == {"title": "Welcome!"}
    
    # --- Test get_type_by_key ---
    comp_type = registry.get_type_by_key("embed_welcome")
    assert comp_type == "embed"

@pytest.mark.asyncio
async def test_get_definition_and_type_by_key_not_found(registry: ComponentRegistry, mocker):
    """Test get_definition_by_key and get_type_by_key when the key is not found."""
    mock_logger_warning = mocker.patch("app.bot.infrastructure.config.registries.component_registry.logger.warning")
    # Initialize with empty DB result
    mock_repo_instance = AsyncMock(spec=DashboardComponentDefinitionRepositoryImpl)
    mock_repo_instance.list_definitions.return_value = []
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.DashboardComponentDefinitionRepositoryImpl",
        return_value=mock_repo_instance
    )
    mock_session = AsyncMock()
    mocker.patch(
        "app.bot.infrastructure.config.registries.component_registry.session_context",
        return_value=mock_session
    )
    mock_session.__aenter__.return_value = mock_session
    mock_bot = MagicMock()
    await registry.initialize(mock_bot)

    # --- Test get_definition_by_key ---
    definition = registry.get_definition_by_key("nonexistent_key")
    assert definition is None
    mock_logger_warning.assert_any_call("Component definition not found in loaded DB definitions for key: 'nonexistent_key'")
    
    # --- Test get_type_by_key ---
    comp_type = registry.get_type_by_key("nonexistent_key")
    assert comp_type is None
    mock_logger_warning.assert_any_call("Component type not found in loaded DB definitions for key: 'nonexistent_key'")
    
    assert mock_logger_warning.call_count == 2 # Called once for each get_*


def test_get_all_component_types(registry: ComponentRegistry):
    """Test retrieving all registered component types."""
    registry.register_component("embed", MockEmbedComponent, "Test Embed")
    registry.register_component("button", MockButtonComponent, "Test Button")
    
    types = registry.get_all_component_types()
    assert isinstance(types, list)
    assert len(types) == 2
    assert "embed" in types
    assert "button" in types

def test_has_component(registry: ComponentRegistry):
    """Test checking if a component type is registered."""
    registry.register_component("embed", MockEmbedComponent, "Test Embed")
    
    assert registry.has_component("embed") is True
    assert registry.has_component("button") is False
    

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import nextcord

# Import the class to be tested
from app.bot.interfaces.dashboards.controller.dashboard_controller import DashboardController

# Import base component for mocking
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

# Mock Component Classes
class MockEmbedComponent(BaseComponent):
    COMPONENT_TYPE = "embed"
    def __init__(self, bot, instance_config):
        # Manually set config for testing, bypassing BaseComponent.__init__ logic
        self.bot = bot
        self.config = instance_config # Store the passed instance config directly
        self.build_called = False
        self.built_object = None
        
    def build(self):
        """Placeholder build method required by BaseComponent."""
        self.build_called = True
        # Use self.config which should now be set
        self.built_object = nextcord.Embed(title=self.config.get('settings', {}).get('title', "Default Mock Title"))
        return self.built_object

    @classmethod
    def deserialize(cls, data: dict, bot=None) -> 'MockEmbedComponent':
        # Basic placeholder implementation for testing
        return cls(bot=bot, instance_config=data)

class MockButtonComponent(BaseComponent):
    COMPONENT_TYPE = "button"
    def __init__(self, bot, instance_config):
        # Manually set config for testing, bypassing BaseComponent.__init__ logic
        self.bot = bot
        self.config = instance_config # Store the passed instance config directly
        self.add_to_view_called = False
        self.built_object = None

    async def add_to_view(self, view, data, config):
        self.add_to_view_called = True
        # Use self.config which should now be set
        self.built_object = nextcord.ui.Button(label=self.config.get('settings', {}).get('label', "Default Mock Label"))
        view.add_item(self.built_object)

    @classmethod
    def deserialize(cls, data: dict, bot=None) -> 'MockButtonComponent':
        # Basic placeholder implementation for testing
        return cls(bot=bot, instance_config=data)

    def build(self):
        """Placeholder build method required by BaseComponent."""
        # Buttons typically don't build a single object like embeds,
        # they are added via add_to_view. Return None or a simple mock.
        return None 

# Fixtures
@pytest.fixture
def mock_bot():
    """Fixture to create a mock bot object with component registry."""
    bot = MagicMock()
    bot.component_registry = MagicMock() # Will be configured by mock_component_registry
    # Add other bot mocks if needed by controller methods
    bot.get_channel = MagicMock(return_value=AsyncMock(spec=nextcord.TextChannel))
    bot.user = MagicMock()
    bot.user.id = 12345
    return bot

@pytest.fixture
def mock_component_registry(mock_bot): # Inject mock_bot to attach registry
    """Fixture to create a mock ComponentRegistry."""
    registry = MagicMock()
    
    # --- Default successful lookups ---
    # Mock get_definition_by_key to return a basic wrapper (used by build_embed)
    registry.get_definition_by_key.side_effect = lambda key: {'type': key} if key == 'embed' else None # Only needed for embed here
    
    # Mock get_type_by_key to return the type string (used by add_component_to_view)
    registry.get_type_by_key.side_effect = lambda key: key if key in ['embed', 'button'] else None
    
    # Mock get_component_class (expects type string)
    def get_class_side_effect(comp_type):
        if comp_type == 'embed':
            return MockEmbedComponent
        if comp_type == 'button':
            return MockButtonComponent
        return None
    registry.get_component_class.side_effect = get_class_side_effect
    
    # Attach the configured registry to the mock bot
    mock_bot.component_registry = registry
    return registry

@pytest.fixture
def dashboard_controller(mock_bot, mock_component_registry):
    """Fixture to create a DashboardController instance with mocks."""
    # Basic minimal config for initialization
    controller = DashboardController(
        dashboard_id="test_dash_1",
        channel_id=12345,
        dashboard_type="test_type",
        bot=mock_bot,
        config={}, # Test methods will set specific configs
        guild_id=67890
    )
    # Ensure registry is attached (redundant if mock_bot fixture does it, but safe)
    controller.component_registry = mock_component_registry 
    return controller

# Test Class
class TestDashboardControllerBuild:
    """Tests for the build_embed and build_view methods of DashboardController."""

    # --- build_embed Tests ---
    @pytest.mark.asyncio
    async def test_build_embed_success(self, dashboard_controller, mock_component_registry):
        """Test successful embed building."""
        dashboard_controller.config = {
            'components': [
                {'component_key': 'embed', 'instance_id': 'embed1', 'settings': {'title': 'Test Embed'}},
                {'component_key': 'button', 'instance_id': 'btn1'}
            ]
        }
        # No longer need to patch BaseComponent.__init__ as we manually set config in mocks
        embed = await dashboard_controller.build_embed({}) # Pass empty data dict
        
        assert isinstance(embed, nextcord.Embed)
        assert embed.title == 'Test Embed' # Title comes from settings in instance_config
        # Verify registry was used
        mock_component_registry.get_definition_by_key.assert_called_with('embed')
        mock_component_registry.get_component_class.assert_called_with('embed')

    @pytest.mark.asyncio
    async def test_build_embed_no_embed_component_in_config(self, dashboard_controller):
        """Test build_embed when no component with type 'embed' is in config."""
        dashboard_controller.config = {
            'components': [
                {'component_key': 'button', 'instance_id': 'btn1'}
            ]
        }
        embed = await dashboard_controller.build_embed({})
        assert embed is None # Expecting None when no embed component found

    @pytest.mark.asyncio
    async def test_build_embed_registry_unavailable(self, dashboard_controller):
        """Test build_embed when component_registry is None."""
        dashboard_controller.component_registry = None
        dashboard_controller.config = {'components': [{'component_key': 'embed'}]}
        
        embed = await dashboard_controller.build_embed({})
        assert isinstance(embed, nextcord.Embed)
        assert "❌ Error" in embed.title
        assert "Component Registry unavailable" in embed.description

    @pytest.mark.asyncio
    async def test_build_embed_registry_missing_type(self, dashboard_controller, mock_component_registry):
        """Test build_embed when registry does not have the 'embed' type class."""
        mock_component_registry.get_component_class.side_effect = lambda comp_type: None # Simulate missing class
        dashboard_controller.config = {'components': [{'component_key': 'embed'}]}
        
        embed = await dashboard_controller.build_embed({})
        assert isinstance(embed, nextcord.Embed)
        assert "❌ Error" in embed.title
        assert "Embed component class not found" in embed.description

    @pytest.mark.asyncio
    async def test_build_embed_component_build_fails(self, dashboard_controller, mock_component_registry):
        """Test build_embed when the component's build method fails."""
        # Patch only the build method now
        with patch.object(MockEmbedComponent, 'build', side_effect=Exception("Build Error")) as mock_build:
            
            dashboard_controller.config = {'components': [{'component_key': 'embed', 'instance_id': 'embed_fail'}]}
            embed = await dashboard_controller.build_embed({})
        
            assert isinstance(embed, nextcord.Embed)
            assert "❌ Error" in embed.title
            assert "Error building dashboard content (embed)." in embed.description
            mock_build.assert_called_once()

    # --- build_view Tests ---
    @pytest.mark.asyncio
    async def test_build_view_success(self, dashboard_controller, mock_component_registry):
        """Test successful view building with interactive components."""
        dashboard_controller.config = {
            'components': [
                {'component_key': 'embed', 'instance_id': 'embed1'},
                {'component_key': 'button', 'instance_id': 'btn1', 'settings': {'label': 'Test Button'}}
            ],
            'interactive_components': ['btn1'] # Only btn1 is interactive
        }
        # No longer need to patch BaseComponent.__init__
        view = await dashboard_controller.build_view({}) # Pass empty data

        assert isinstance(view, nextcord.ui.View)
        assert len(view.children) == 1
        button_item = view.children[0]
        assert isinstance(button_item, nextcord.ui.Button)
        assert button_item.label == 'Test Button' # Label comes from settings in instance_config
        # Verify registry was used for the button
        # Note: This might still fail if registry interaction is wrong
        mock_component_registry.get_type_by_key.assert_called_with('button')
        mock_component_registry.get_component_class.assert_called_with('button')

    @pytest.mark.asyncio
    async def test_build_view_no_interactive_components(self, dashboard_controller):
        """Test build_view returns None when no interactive components are specified."""
        dashboard_controller.config = {
            'components': [
                {'component_key': 'embed', 'instance_id': 'embed1'}
            ],
            'interactive_components': [] # Empty list
        }
        view = await dashboard_controller.build_view({})
        assert view is None

        dashboard_controller.config = {'components': []} # No components at all
        view = await dashboard_controller.build_view({})
        assert view is None

    @pytest.mark.asyncio
    async def test_build_view_component_add_fails(self, dashboard_controller, mock_component_registry):
        """Test build_view when a component fails to be added (e.g., add_to_view error)."""
        # Patch only the add_to_view method
        with patch.object(MockButtonComponent, 'add_to_view', side_effect=Exception("Add Error")) as mock_add:
            
            dashboard_controller.config = {
                'components': [{'component_key': 'button', 'instance_id': 'btn_fail'}],
                'interactive_components': ['btn_fail']
            }
            view = await dashboard_controller.build_view({})

            # Expect None because the only component failed to add, resulting in an empty view
            assert view is None 
            mock_add.assert_awaited_once() 

    # TODO: Add more specific tests if needed (e.g., component config missing, registry missing specific types during view build) 
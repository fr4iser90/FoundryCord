"""Factory for creating and managing dashboard components."""
from typing import Dict, Any, Type, Optional
import inspect
import importlib
import pkgutil
import os

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ComponentRegistryFactory:
    """Factory for creating and managing dashboard components."""
    
    def __init__(self, bot):
        self.bot = bot
        self.components = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the component registry."""
        try:
            # Auto-discover components
            await self._discover_components()
            
            self.initialized = True
            logger.info(f"Component Registry initialized with {len(self.components)} components")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Component Registry: {e}")
            return False
            
    async def _discover_components(self):
        """Automatically discover and register components."""
        try:
            # Base component path
            base_path = "app.bot.interfaces.dashboards.components"
            base_module = importlib.import_module(base_path)
            base_dir = os.path.dirname(base_module.__file__)
            
            # Scan for component modules
            for _, name, is_pkg in pkgutil.iter_modules([base_dir]):
                if name.startswith("_"):
                    continue
                    
                try:
                    # Import module
                    module = importlib.import_module(f"{base_path}.{name}")
                    
                    # Find component classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (inspect.isclass(attr) and 
                            attr_name.endswith("Component") and 
                            hasattr(attr, "render_to_embed") and
                            hasattr(attr, "create_ui_component")):
                            
                            # Register component
                            component_type = name.lower()
                            self.register_component(component_type, attr)
                            
                except Exception as e:
                    logger.error(f"Error loading component module {name}: {e}")
                    
            return True
        except Exception as e:
            logger.error(f"Error discovering components: {e}")
            return False
            
    def register_component(self, component_type: str, component_class: Type):
        """Register a component with the registry."""
        self.components[component_type] = component_class
        logger.debug(f"Registered component: {component_type}")
        
    def get_component(self, component_type: str) -> Optional[Type]:
        """Get a component class by type."""
        return self.components.get(component_type)
        
    def create_component(self, component_type: str, config: Dict[str, Any]) -> Optional[Any]:
        """Create a component instance."""
        try:
            component_class = self.get_component(component_type)
            if not component_class:
                logger.warning(f"Component type not found: {component_type}")
                return None
                
            return component_class(self.bot, config)
        except Exception as e:
            logger.error(f"Error creating component {component_type}: {e}")
            return None 
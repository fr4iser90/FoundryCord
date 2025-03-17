"""Base factory for UI components with abstract methods properly implemented."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseFactory(ABC):
    """Abstract base factory for UI components."""
    
    @abstractmethod
    def create(self, *args, **kwargs):
        """Create a component instance."""
        pass

# Note: This is an abstract class that should not be instantiated directly 
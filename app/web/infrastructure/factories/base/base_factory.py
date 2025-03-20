from abc import ABC, abstractmethod
from typing import Any

class BaseFactory(ABC):
    """Base factory interface for web services"""
    
    @abstractmethod
    def create(self) -> Any:
        """Create and return a service instance"""
        pass 
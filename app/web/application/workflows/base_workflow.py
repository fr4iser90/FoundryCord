from abc import ABC, abstractmethod

class BaseWorkflow(ABC):
    """Base class for all web workflows"""
    
    @abstractmethod
    async def execute(self):
        """Execute the workflow"""
        pass 
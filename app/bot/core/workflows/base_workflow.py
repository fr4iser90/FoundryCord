import logging
from typing import Optional, List
import nextcord

logger = logging.getLogger("homelab.bot")

class BaseWorkflow:
    """Base class for all workflows"""
    
    def __init__(self, bot=None):
        self.name = "base"  # Must be overridden by subclasses
        self.bot = bot
        self.dependencies = []  # List of workflow names this workflow depends on
    
    async def initialize(self) -> bool:
        """Initialize the workflow - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement initialize()")
    
    async def cleanup(self) -> None:
        """Cleanup resources used by the workflow - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement cleanup()")
    
    def add_dependency(self, workflow_name: str) -> None:
        """Add a dependency to this workflow"""
        if workflow_name not in self.dependencies:
            self.dependencies.append(workflow_name)
    
    def get_dependencies(self) -> List[str]:
        """Get all dependencies for this workflow"""
        return self.dependencies

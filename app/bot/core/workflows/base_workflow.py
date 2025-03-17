from abc import ABC, abstractmethod
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
import logging
from typing import Optional

class BaseWorkflow(ABC):
    """Base class for all workflows"""
    
    def __init__(self, bot=None):
        """Initialize the workflow with optional bot reference"""
        self.name = "base"
        self.is_initialized = False
        self.bot = bot
        
    @abstractmethod
    async def initialize(self):
        """Initialize the workflow"""
        self.is_initialized = True
        return True
        
    @abstractmethod
    async def cleanup(self):
        """Clean up resources"""
        pass

from abc import ABC, abstractmethod
from app.bot.infrastructure.logging import logger

class BaseWorkflow(ABC):
    def __init__(self, bot):
        self.bot = bot
        
    @abstractmethod
    async def initialize(self):
        """Initialize workflow components"""
        pass
        
    @abstractmethod
    async def cleanup(self):
        """Cleanup workflow resources"""
        pass

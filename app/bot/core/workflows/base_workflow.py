from abc import ABC, abstractmethod
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

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

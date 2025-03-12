from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.web.server import WebInterfaceServer

class WebInterfaceWorkflow(BaseWorkflow):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "Web Interface"
        
    async def initialize(self):
        """Initialize web interface components"""
        try:
            logger.info("Initializing web interface...")
            if not self.bot.env_config.enable_webinterface:
                logger.info("Web interface is disabled. Skipping initialization.")
                return
                
            # Create web server instance
            self.bot.web_server = WebInterfaceServer(self.bot)
            
            # Start web server
            await self.bot.web_server.start()
            
            logger.info("Web interface initialized successfully")
        except Exception as e:
            logger.error(f"Web interface initialization failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup web interface resources"""
        try:
            if hasattr(self.bot, 'web_server'):
                await self.bot.web_server.stop()
        except Exception as e:
            logger.error(f"Web interface cleanup failed: {e}")
            
    async def execute(self) -> None:
        """Execute web interface initialization"""
        await self.initialize()
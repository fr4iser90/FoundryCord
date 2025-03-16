import asyncio
from aiohttp import web
import nextcord
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class WebInterfaceServer:
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.config = bot.env_config
        
    async def setup_routes(self):
        # Import routes here to avoid circular imports
        from app.bot.infrastructure.web.routes import setup_routes
        setup_routes(self.app, self.bot)
        
    async def setup_middleware(self):
        # Import middleware here to avoid circular imports
        from app.bot.infrastructure.web.auth_middleware import setup_middleware
        setup_middleware(self.app, self.bot)
        
    async def start(self):
        if not self.config.enable_webinterface:
            logger.info("Web interface is disabled. Skipping initialization.")
            return
            
        try:
            logger.info("Starting web interface server...")
            await self.setup_middleware()
            await self.setup_routes()
            
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(
                self.runner, 
                self.config.webinterface_host, 
                self.config.webinterface_port
            )
            
            await self.site.start()
            logger.info(f"Web interface running at http://{self.config.webinterface_host}:{self.config.webinterface_port}")
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            
    async def stop(self):
        if self.runner:
            logger.info("Stopping web interface server...")
            await self.runner.cleanup()
            logger.info("Web interface server stopped")
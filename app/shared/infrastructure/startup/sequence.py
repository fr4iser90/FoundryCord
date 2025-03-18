"""Startup sequence manager."""
import logging
from typing import List, Dict, Any

logger = logging.getLogger("homelab.bot")

class StartupSequence:
    """Manages the startup sequence for different container types."""
    
    def __init__(self, container):
        """Initialize startup sequence with dependency container."""
        self.container = container
        
    async def run_bot_sequence(self) -> bool:
        """Run the bot startup sequence."""
        try:
            # Define the bot startup sequence
            sequence = [
                "database",
                "category", 
                "channel", 
                "dashboard", 
                "task"
            ]
            
            logger.info(f"Starting bot initialization sequence: {sequence}")
            
            # Initialize database service
            from app.shared.infrastructure.database.service import DatabaseService
            db_service = DatabaseService(self.container.db_connection)
            self.container.register("database_service", db_service)
            
            # Initialize each workflow in sequence
            for workflow in sequence:
                logger.info(f"Initializing workflow: {workflow}")
                
                if workflow == "database":
                    # Database is already initialized
                    logger.info("Database workflow initialized successfully")
                    
                elif workflow == "category":
                    from app.bot.application.services.category.category_setup_service import CategorySetupService
                    category_service = CategorySetupService(db_service)
                    await category_service.initialize()
                    self.container.register("category_service", category_service)
                    logger.info("Category workflow initialized successfully")
                    
                elif workflow == "channel":
                    from app.bot.application.services.channel.channel_setup_service import ChannelSetupService
                    channel_service = ChannelSetupService(
                        db_service, 
                        self.container.get("category_service")
                    )
                    await channel_service.initialize()
                    self.container.register("channel_service", channel_service)
                    logger.info("Channel workflow initialized successfully")
                    
                elif workflow == "dashboard":
                    from app.bot.application.services.dashboard.dashboard_service import DashboardService
                    dashboard_service = DashboardService(db_service)
                    await dashboard_service.initialize()
                    self.container.register("dashboard_service", dashboard_service)
                    logger.info("Dashboard workflow initialized successfully")
                    
                elif workflow == "task":
                    from app.bot.application.services.task.task_service import TaskService
                    task_service = TaskService(db_service)
                    await task_service.initialize()
                    self.container.register("task_service", task_service)
                    logger.info("Task workflow initialized successfully")
                    
            logger.info("Bot initialization sequence completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization sequence failed: {str(e)}")
            return False
            
    async def run_web_sequence(self) -> bool:
        """Run the web startup sequence."""
        try:
            # Define the web startup sequence
            sequence = [
                "database",
                "security",
                "api"
            ]
            
            logger.info(f"Starting web initialization sequence: {sequence}")
            
            # Initialize database service
            from app.shared.infrastructure.database.service import DatabaseService
            db_service = DatabaseService(self.container.db_connection)
            self.container.register("database_service", db_service)
            
            # Initialize each component in sequence
            for component in sequence:
                logger.info(f"Initializing component: {component}")
                
                if component == "database":
                    # Database is already initialized
                    logger.info("Database component initialized successfully")
                    
                elif component == "security":
                    from app.web.application.services.security.security_service import SecurityService
                    security_service = SecurityService(db_service)
                    await security_service.initialize()
                    self.container.register("security_service", security_service)
                    logger.info("Security component initialized successfully")
                    
                elif component == "api":
                    from app.web.application.services.api.api_service import ApiService
                    api_service = ApiService(
                        db_service,
                        self.container.get("security_service")
                    )
                    await api_service.initialize()
                    self.container.register("api_service", api_service)
                    logger.info("API component initialized successfully")
                    
            logger.info("Web initialization sequence completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Web initialization sequence failed: {str(e)}")
            return False
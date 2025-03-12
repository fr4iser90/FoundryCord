from app.bot.infrastructure.logging import logger

class ServiceResolver:
    @staticmethod
    async def resolve_dashboard_setup(bot, dashboard_type):
        """Resolves dashboard setup function while respecting the factory pattern"""
        try:
            # Dynamic resolution of setup function to avoid circular imports
            module_name = f"application.services.dashboard.{dashboard_type.lower()}_dashboard_service"
            setup_attr = "setup"
            
            # Import module dynamically
            module = __import__(module_name, fromlist=[setup_attr])
            setup_func = getattr(module, setup_attr, None)
            
            if not setup_func:
                logger.error(f"Setup function not found for dashboard type {dashboard_type}")
                return None
                
            return setup_func
        except ImportError as e:
            logger.error(f"Failed to resolve setup function for {dashboard_type}: {e}")
            return None

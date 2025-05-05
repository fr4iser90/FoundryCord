from app.web.core.workflows.base_workflow import BaseWorkflow
from app.web.core.lifecycle_manager import WebLifecycleManager
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

class WebServiceWorkflow(BaseWorkflow):
    def __init__(self):
        self.lifecycle_manager = WebLifecycleManager()

    async def execute(self):
        """Execute service initialization workflow"""
        try:
            await self.lifecycle_manager.initialize_services()
            logger.info("Web service workflow completed successfully")
        except Exception as e:
            logger.error(f"Web service workflow failed: {e}")
            raise 
from typing import Dict, List, Optional
from app.web.core.workflows.base_workflow import BaseWorkflow
from app.shared.interfaces.logging.api import get_web_logger
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory

logger = get_web_logger()

class WebWorkflowManager:
    """Manages web application workflows."""
    
    def __init__(self):
        """Initialize the workflow manager."""
        self.service_factory = None
        self.workflows = {}  # Geändert von Liste zu Dictionary mit Workflow-Namen als Schlüssel
        self.initialized = False
        self.initialization_order = []
        
    def initialize(self, service_factory: WebServiceFactory):
        """Initialize with service factory."""
        self.service_factory = service_factory
        
    async def initialize_workflows(self):
        """Initialize all workflows."""
        try:
            # Hier könnten wir default-Workflows registrieren
            from app.web.core.workflows.service_workflow import WebServiceWorkflow
            self.register_workflow(WebServiceWorkflow(), "service_workflow", [])
            
            # Setze eine Standard-Initialisierungsreihenfolge
            self.set_initialization_order(["service_workflow"])
            
            logger.info("Web workflows initialized")
        except Exception as e:
            logger.error(f"Failed to initialize workflows: {e}")
            raise
    
    async def execute_startup_workflow(self):
        """Execute the startup workflow sequence"""
        try:
            logger.info("Executing startup workflow sequence")
            await self.initialize_all()
            logger.info("Startup workflow sequence completed")
            return True
        except Exception as e:
            logger.error(f"Startup workflow sequence failed: {e}")
            return False
            
    async def start_workflows(self):
        """Start all workflows."""
        try:
            # Start workflows here
            logger.info("Web workflows started")
        except Exception as e:
            logger.error(f"Failed to start workflows: {e}")
            raise
            
    async def stop_workflows(self):
        """Stop all workflows."""
        try:
            # Stop workflows here
            logger.info("Web workflows stopped")
        except Exception as e:
            logger.error(f"Failed to stop workflows: {e}")
            raise

    def register_workflow(self, workflow: BaseWorkflow, name: str, dependencies: List[str] = None):
        """Register a workflow with optional dependencies"""
        self.workflows[name] = {
            'instance': workflow,
            'dependencies': dependencies or [],
            'initialized': False
        }
        logger.debug(f"Registered workflow: {name}")
    
    def set_initialization_order(self, order: List[str]):
        """Set explicit initialization order for workflows"""
        self.initialization_order = [name for name in order if name in self.workflows]
        logger.info(f"Set initialization order: {self.initialization_order}")
    
    async def initialize_workflow(self, name: str) -> bool:
        """Initialize a single workflow and its dependencies"""
        if name not in self.workflows:
            logger.error(f"Workflow {name} not found")
            return False
            
        workflow_data = self.workflows[name]
        
        if workflow_data['initialized']:
            return True
            
        for dep_name in workflow_data['dependencies']:
            if not await self.initialize_workflow(dep_name):
                return False
        
        try:
            await workflow_data['instance'].execute()
            workflow_data['initialized'] = True
            logger.info(f"Workflow {name} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing workflow {name}: {e}")
            return False
    
    async def initialize_all(self) -> bool:
        """Initialize all workflows in the correct order"""
        logger.info("Initializing all webworkflows")
        
        for name in self.initialization_order:
            if not await self.initialize_workflow(name):
                return False
        
        self.initialized = True
        return True
    
    def get_workflow(self, name: str) -> Optional[BaseWorkflow]:
        """Get a workflow by name"""
        if name not in self.workflows:
            return None
        return self.workflows[name]['instance'] 
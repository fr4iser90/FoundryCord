from typing import Dict, List, Optional
from app.web.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class WebWorkflowManager:
    """Manages web workflows, following bot pattern"""
    
    def __init__(self):
        self.workflows = {}
        self.initialized = False
        self.initialization_order = []
    
    def register_workflow(self, workflow: BaseWorkflow, dependencies: List[str] = None):
        """Register a workflow with optional dependencies"""
        name = workflow.name
        self.workflows[name] = {
            'instance': workflow,
            'dependencies': dependencies or [],
            'initialized': False
        }
        logger.debug(f"Registered workflow: {name}")
        
        if name not in self.initialization_order:
            self.initialization_order.append(name)
    
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
        logger.info("Initializing all workflows")
        
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
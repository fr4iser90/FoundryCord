import logging
import asyncio
from typing import Dict, List, Type, Optional
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class BotWorkflowManager:
    """
    Central manager for all bot workflows with standardized initialization.
    """
    
    def __init__(self):
        self.workflows = {}  # Dict[str, Dict] where inner dict has 'instance', 'dependencies', 'initialized'
        self.initialized = False
        self.initialization_order = []
        
    def register_workflow(self, workflow: BaseWorkflow, dependencies: List[str] = None):
        """Register a workflow with optional dependencies"""
        name = workflow.name
        
        # Store workflow with its metadata
        self.workflows[name] = {
            'instance': workflow,
            'dependencies': dependencies or workflow.get_dependencies() or [],
            'initialized': False
        }
        logger.debug(f"Registered workflow: {name}")
        
        # Update initialization order if needed
        if name not in self.initialization_order:
            self.initialization_order.append(name)
            
    def set_initialization_order(self, order: List[str]):
        """Set explicit initialization order for workflows"""
        # Validate that all workflows in order are registered
        for name in order:
            if name not in self.workflows:
                logger.warning(f"Workflow {name} in initialization order is not registered")
                
        # Set the order, but only for registered workflows
        self.initialization_order = [name for name in order if name in self.workflows]
        logger.info(f"Set initialization order: {self.initialization_order}")
    
    async def initialize_workflow(self, name: str) -> bool:
        """Initialize a single workflow and its dependencies"""
        if name not in self.workflows:
            logger.error(f"Workflow {name} not found")
            return False
            
        workflow_data = self.workflows[name]
        
        # Skip if already initialized
        if workflow_data['initialized']:
            return True
            
        # Initialize dependencies first
        for dep_name in workflow_data['dependencies']:
            if dep_name not in self.workflows:
                logger.error(f"Dependency {dep_name} for workflow {name} not found")
                return False
                
            # Initialize the dependency
            if not await self.initialize_workflow(dep_name):
                logger.error(f"Failed to initialize dependency {dep_name} for workflow {name}")
                return False
        
        # Now initialize the workflow itself
        logger.info(f"Initializing workflow: {name}")
        try:
            success = await workflow_data['instance'].initialize()
            if success:
                workflow_data['initialized'] = True
                logger.info(f"Workflow {name} initialized successfully")
                return True
            else:
                logger.error(f"Workflow {name} initialization returned False")
                return False
        except Exception as e:
            logger.error(f"Error initializing workflow {name}: {e}")
            return False
    
    async def initialize_all(self) -> bool:
        """Initialize all workflows in the correct order"""
        logger.info("Initializing all bot workflows")
        
        all_initialized = True
        failed = []
        
        # Initialize in the specified order
        for name in self.initialization_order:
            if not await self.initialize_workflow(name):
                all_initialized = False
                failed.append(name)
                logger.error(f"Failed to initialize workflow: {name}")
        
        self.initialized = all_initialized
        
        if not all_initialized:
            logger.error(f"Some workflows failed to initialize: {failed}")
            
        return all_initialized
    
    async def cleanup_all(self):
        """Cleanup all workflows in reverse initialization order"""
        logger.info("Cleaning up all workflows")
        
        # Reverse the order for proper teardown
        for name in reversed(self.initialization_order):
            if name not in self.workflows:
                continue
                
            workflow_data = self.workflows[name]
            if not workflow_data['initialized']:
                continue
                
            # Cleanup the workflow
            logger.info(f"Cleaning up workflow: {name}")
            try:
                await workflow_data['instance'].cleanup()
                workflow_data['initialized'] = False
                logger.info(f"Workflow {name} cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up workflow {name}: {e}")
        
        self.initialized = False
        logger.info("All workflows cleaned up")
    
    def get_workflow(self, name: str) -> Optional[BaseWorkflow]:
        """Get a workflow by name"""
        if name not in self.workflows:
            return None
        return self.workflows[name]['instance']
    
    def get_initialization_status(self) -> Dict[str, bool]:
        """Get initialization status of all workflows"""
        return {name: data['initialized'] for name, data in self.workflows.items()}
    
    def is_initialized(self) -> bool:
        """Check if all workflows are initialized"""
        return self.initialized 
    
    async def initialize_workflow_for_guild(self, workflow_name: str, guild_id: str) -> bool:
        """Initialize a specific workflow for a specific guild"""
        if workflow_name not in self.workflows:
            logger.error(f"Workflow {workflow_name} not registered")
            return False
        
        workflow_data = self.workflows[workflow_name]
        workflow = workflow_data['instance']
        
        # Check if the workflow has a guild-specific initialization method
        if hasattr(workflow, 'initialize_for_guild'):
            logger.info(f"Initializing workflow {workflow_name} for guild {guild_id}")
            try:
                success = await workflow.initialize_for_guild(guild_id)
                return success
            except Exception as e:
                logger.error(f"Error initializing workflow {workflow_name} for guild {guild_id}: {e}")
                return False
        else:
            # If no guild-specific method, use the standard initialization
            return workflow_data['initialized'] 
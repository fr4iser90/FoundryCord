import logging
import asyncio
from typing import Dict, List, Type, Optional
from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
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
        
        # Store workflow with its metadata_json
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
        """Initialize a single workflow globally"""
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
        """Initialize all workflows globally"""
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

    async def initialize_guild(self, guild_id: str, workflow_names: Optional[List[str]] = None) -> Dict[str, bool]:
        """Initialize specific or all workflows for a guild"""
        results = {}
        
        # If no specific workflows specified, use all
        if workflow_names is None:
            workflow_names = self.initialization_order
        
        for name in workflow_names:
            if name not in self.workflows:
                logger.error(f"Workflow {name} not found")
                results[name] = False
                continue
                
            workflow = self.workflows[name]['instance']
            
            # Skip if workflow doesn't require guild initialization
            if not workflow.requires_guild_approval:
                results[name] = True
                continue
                
            # Initialize workflow for guild
            try:
                success = await workflow.initialize_for_guild(guild_id)
                results[name] = success
                if not success:
                    logger.error(f"Failed to initialize workflow {name} for guild {guild_id}")
            except Exception as e:
                logger.error(f"Error initializing workflow {name} for guild {guild_id}: {e}")
                results[name] = False
                
        return results

    async def disable_guild(self, guild_id: str, workflow_names: Optional[List[str]] = None) -> None:
        """Disable specific or all workflows for a guild"""
        if workflow_names is None:
            workflow_names = self.initialization_order
            
        for name in workflow_names:
            if name in self.workflows:
                workflow = self.workflows[name]['instance']
                await workflow.disable_for_guild(guild_id)

    def get_workflow(self, name: str) -> Optional[BaseWorkflow]:
        """Get a workflow by name"""
        if name not in self.workflows:
            return None
        return self.workflows[name]['instance']
    
    def get_guild_workflow_status(self, guild_id: str) -> Dict[str, WorkflowStatus]:
        """Get status of all workflows for a specific guild"""
        return {
            name: self.workflows[name]['instance'].get_guild_status(guild_id)
            for name in self.workflows
        }
    
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup all workflows for a specific guild"""
        for name in reversed(self.initialization_order):
            if name in self.workflows:
                workflow = self.workflows[name]['instance']
                await workflow.cleanup_guild(guild_id)
    
    async def cleanup_all(self):
        """Cleanup all workflows"""
        logger.info("Cleaning up all workflows")
        
        # Cleanup in reverse order
        for name in reversed(self.initialization_order):
            if name in self.workflows:
                workflow = self.workflows[name]['instance']
                try:
                    await workflow.cleanup()
                    logger.info(f"Cleaned up workflow: {name}")
                except Exception as e:
                    logger.error(f"Error cleaning up workflow {name}: {e}")
        
        self.initialized = False 
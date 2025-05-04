import logging
from typing import Optional, List, Dict
import nextcord
from enum import Enum

logger = logging.getLogger("homelab.bot")

class WorkflowStatus(Enum):
    """Status of a workflow for a specific guild"""
    PENDING = "pending"      # Waiting for initialization
    INITIALIZING = "initializing"  # Currently initializing
    ACTIVE = "active"       # Successfully initialized and running
    DISABLED = "disabled"    # Explicitly disabled
    FAILED = "failed"       # Initialization failed
    UNAUTHORIZED = "unauthorized"  # Not authorized (guild not approved)

class BaseWorkflow:
    """Base class for all workflows"""
    
    def __init__(self, name: str):
        self.name = name  # Must be overridden by subclasses
        self.dependencies = []  # List of workflow names this workflow depends on
        self.guild_status = {}  # Dict[str, WorkflowStatus] tracking status per guild
        self.requires_guild_approval = True  # Whether this workflow requires guild approval
        self.auto_initialize = True  # Whether to automatically initialize for approved guilds
        
    def add_dependency(self, workflow_name: str) -> None:
        """Add a dependency to this workflow"""
        if workflow_name not in self.dependencies:
            self.dependencies.append(workflow_name)
    
    def get_dependencies(self) -> List[str]:
        """Get all dependencies for this workflow"""
        return self.dependencies

    async def initialize(self) -> bool:
        """Initialize the workflow globally"""
        logger.debug(f"Initializing workflow {self.name} globally")
        return True

    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        try:
            # Update status to initializing
            self.guild_status[guild_id] = WorkflowStatus.INITIALIZING
            logger.debug(f"Initializing workflow {self.name} for guild {guild_id}")
            
            # Check dependencies
            if not await self._check_dependencies(guild_id):
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
            
            # Run the actual initialization
            success = await self._initialize_guild(guild_id)
            
            # Update status based on result
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE if success else WorkflowStatus.FAILED
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing workflow {self.name} for guild {guild_id}: {e}")
            self.guild_status[guild_id] = WorkflowStatus.FAILED
            return False

    async def _initialize_guild(self, guild_id: str) -> bool:
        """
        Actual guild initialization logic - must be implemented by subclasses
        Returns True if successful, False otherwise
        """
        return True

    async def _check_dependencies(self, guild_id: str) -> bool:
        """Check if all dependencies are initialized for this guild"""
        if not hasattr(self, 'bot') or not hasattr(self.bot, 'workflow_manager'):
            return True
            
        for dep_name in self.dependencies:
            workflow = self.bot.workflow_manager.get_workflow(dep_name)
            if not workflow:
                logger.error(f"Dependency {dep_name} not found for workflow {self.name}")
                return False
                
            status = workflow.get_guild_status(guild_id)
            if status != WorkflowStatus.ACTIVE:
                logger.error(f"Dependency {dep_name} not active for guild {guild_id} (status: {status})")
                return False
                
        return True

    def get_guild_status(self, guild_id: str) -> WorkflowStatus:
        """Get the current status of this workflow for a specific guild"""
        return self.guild_status.get(guild_id, WorkflowStatus.PENDING)

    async def disable_for_guild(self, guild_id: str) -> None:
        """Disable this workflow for a specific guild"""
        self.guild_status[guild_id] = WorkflowStatus.DISABLED
        await self.cleanup_guild(guild_id)

    async def enable_for_guild(self, guild_id: str) -> bool:
        """Enable and initialize this workflow for a specific guild"""
        if self.guild_status.get(guild_id) == WorkflowStatus.DISABLED:
            return await self.initialize_for_guild(guild_id)
        return False

    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild - can be overridden by subclasses"""
        if guild_id in self.guild_status:
            del self.guild_status[guild_id]

    async def cleanup(self) -> None:
        """Cleanup all resources"""
        for guild_id in list(self.guild_status.keys()):
            await self.cleanup_guild(guild_id)
        self.guild_status.clear()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' guilds={len(self.guild_status)}>"

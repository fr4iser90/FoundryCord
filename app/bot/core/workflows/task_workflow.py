import logging
import asyncio
from typing import Dict, Any, Optional, List
import nextcord
from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.application.services.project_management.task_service import TaskService

logger = get_bot_logger()

class TaskWorkflow(BaseWorkflow):
    """Workflow for managing scheduled and background tasks"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot):
        super().__init__("task")
        self.bot = bot
        self.database_workflow = database_workflow
        self.tasks = []
        self.running = False
        
        # Add dependencies
        self.add_dependency("database")
        
        # Tasks require guild approval
        self.requires_guild_approval = True
    
    async def initialize(self) -> bool:
        """Initialize the task workflow globally"""
        try:
            logger.info("Initializing task workflow")
            
            self.running = True
            
            # Register background tasks
            self.register_background_tasks()
            
            logger.info("Task workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing task workflow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def cleanup(self):
        """Cleanup resources used by the task workflow"""
        logger.info("Cleaning up task workflow resources")
        
        try:
            # Set running flag to false so tasks can exit
            self.running = False
            
            # Cancel all running tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Clear the task list
            self.tasks.clear()
            
            logger.info("Task workflow resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up task workflow: {e}")
    
    def register_background_tasks(self):
        """Register background tasks to run"""
        # Example of registering a task
        # task = asyncio.create_task(self.some_background_task())
        # self.tasks.append(task)
        pass
    
    async def some_background_task(self):
        """Example of a background task"""
        while self.running:
            try:
                logger.debug("Running background task")
                # Do something periodically
                await asyncio.sleep(60)  # Sleep for 60 seconds
            except asyncio.CancelledError:
                logger.info("Background task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                await asyncio.sleep(60)  # Sleep before retrying

import logging
import asyncio
from typing import Dict, Any, Optional, List
import nextcord
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class TaskWorkflow(BaseWorkflow):
    """Workflow for managing scheduled and background tasks"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "task"
        self.tasks = []
        self.running = False
        self.task_service = None
        self.project_service = None
        
        # Add dependencies
        self.add_dependency("database")
    
    async def initialize(self):
        """Initialize the task workflow"""
        logger.info("Initializing task workflow")
        
        try:
            # Import services
            from app.bot.application.services.project_management.task_service import TaskService
            from app.bot.application.services.project_management.project_service import ProjectService
            
            # Initialize services
            self.task_service = TaskService(self.bot)
            self.project_service = ProjectService(self.bot)
            
            # TaskService hat keine initialize()-Methode, also überspringen wir diesen Aufruf
            # await self.task_service.initialize()
            
            # ProjectService hat möglicherweise auch keine initialize()-Methode
            # await self.project_service.initialize()
            
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
            # Cleanup task service
            if self.task_service and hasattr(self.task_service, 'cleanup'):
                await self.task_service.cleanup()
            
            # Cleanup project service
            if self.project_service and hasattr(self.project_service, 'cleanup'):
                await self.project_service.cleanup()
            
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
    
    def get_task_service(self):
        """Get the task service"""
        return self.task_service
    
    def get_project_service(self):
        """Get the project service"""
        return self.project_service

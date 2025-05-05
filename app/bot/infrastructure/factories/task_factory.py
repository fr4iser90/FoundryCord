"""Task factory for creating and managing background tasks."""
from typing import Dict, Any, Optional, Callable, Awaitable
import asyncio

from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class TaskFactory:
    """Factory for creating and managing background tasks."""
    
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}
        self.initialized = False
    
    def create(self, task_name: str, coro_func: Callable[..., Awaitable], *args, **kwargs):
        """Create and schedule a background task."""
        try:
            # Cancel existing task if it exists
            if task_name in self.tasks and not self.tasks[task_name].done():
                logger.debug(f"Cancelling existing task: {task_name}")
                self.tasks[task_name].cancel()
                
            # Create and schedule the task
            task = asyncio.create_task(coro_func(*args, **kwargs))
            self.tasks[task_name] = task
            
            # Add done callback to clean up task when it's done
            task.add_done_callback(lambda t: self._handle_task_done(task_name, t))
            
            logger.debug(f"Created task: {task_name}")
            return task
            
        except Exception as e:
            logger.error(f"Error creating task {task_name}: {e}")
            return None
    
    def _handle_task_done(self, task_name: str, task):
        """Handle task completion or cancellation."""
        try:
            # Check if task raised an exception
            if task.done() and not task.cancelled():
                exception = task.exception()
                if exception:
                    logger.error(f"Task {task_name} raised an exception: {exception}")
            
            # Clean up task reference
            if task_name in self.tasks and self.tasks[task_name] == task:
                del self.tasks[task_name]
                
        except asyncio.CancelledError:
            logger.debug(f"Task {task_name} was cancelled")
        except Exception as e:
            logger.error(f"Error handling task completion for {task_name}: {e}")
    
    def cancel_task(self, task_name: str) -> bool:
        """Cancel a running task."""
        if task_name in self.tasks and not self.tasks[task_name].done():
            self.tasks[task_name].cancel()
            logger.debug(f"Cancelled task: {task_name}")
            return True
        return False
    
    def cancel_all_tasks(self):
        """Cancel all running tasks."""
        cancelled = 0
        for task_name in list(self.tasks.keys()):
            if self.cancel_task(task_name):
                cancelled += 1
                
        logger.debug(f"Cancelled {cancelled} tasks")
        return cancelled
    
    def get_task(self, task_name: str):
        """Get a running task by name."""
        return self.tasks.get(task_name)
    
    def get_all_tasks(self) -> Dict[str, asyncio.Task]:
        """Get all running tasks."""
        return self.tasks.copy()
    
    def is_task_running(self, task_name: str) -> bool:
        """Check if a task is running."""
        return task_name in self.tasks and not self.tasks[task_name].done() 
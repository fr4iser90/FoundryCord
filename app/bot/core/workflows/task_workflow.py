from .base_workflow import BaseWorkflow
from infrastructure.logging import logger

class TaskWorkflow(BaseWorkflow):
    async def initialize(self):
        """Initialize all task components"""
        try:
            logger.debug("Starting task workflow initialization")
            
            # Initialize registered tasks
            if hasattr(self.bot, 'tasks'):
                for task in self.bot.tasks:
                    try:
                        logger.info(f"Starting task: {task['name']}")
                        await self.bot.task_factory.create_task(
                            task['func'],
                            task['name'],
                            *task.get('args', [])
                        )
                    except Exception as e:
                        logger.error(f"Failed to start task {task['name']}: {e}")
                        raise
                        
            return True
            
        except Exception as e:
            logger.error(f"Task workflow initialization failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup task resources"""
        try:
            logger.debug("Starting task cleanup")
            # Cancel all running tasks
            for task in self.bot.tasks:
                try:
                    if hasattr(task, 'task') and not task['task'].done():
                        task['task'].cancel()
                except Exception as e:
                    logger.error(f"Error cleaning up task {task['name']}: {e}")
        except Exception as e:
            logger.error(f"Task cleanup failed: {e}")

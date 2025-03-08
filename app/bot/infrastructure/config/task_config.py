from typing import List
#from application.tasks.system_status_task import system_status_task
#from application.tasks.cleanup_task import cleanup_task
#from application.tasks.cleanup_dm_task import cleanup_dm_task
from infrastructure.logging import logger

class TaskConfig:
    @staticmethod
    def register_tasks(bot) -> List:
        """Register all background tasks"""
        try:
            return [
#                bot.task_factory.create("System Status", system_status_task),
#                bot.task_factory.create("Cleanup", cleanup_task),
#                bot.task_factory.create("DM Cleanup", cleanup_dm_task),
            ]
        except Exception as e:
            logger.error(f"Failed to register tasks: {e}")
            raise
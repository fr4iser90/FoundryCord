from .base_factory import BaseFactory
from typing import Callable, Dict, Any

class TaskFactory(BaseFactory):
    def create(self, name: str, task_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Create a task component"""
        task = {
            'name': name,
            'func': task_func,
            'args': args,
            'type': 'task',
            'config': kwargs,
            'autostart': kwargs.get('autostart', True)
        }
        self.register(name, task)
        return task
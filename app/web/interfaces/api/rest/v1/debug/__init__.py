from .debug_controller import debug_controller

router = debug_controller.router

__all__ = [
    'debug_controller',
    'router'
] 
from .auth_controller import auth_controller

router = auth_controller.router

__all__ = [
    'auth_controller',
    'router'
] 
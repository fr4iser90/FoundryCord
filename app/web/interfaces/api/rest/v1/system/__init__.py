from .health_controller import HealthController, health_controller

router = health_controller.router

__all__ = ['HealthController', 'router'] 
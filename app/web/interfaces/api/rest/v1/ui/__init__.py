from .layout_controller import layout_controller

# Get the router from the controller instance
router = layout_controller.router

# Export both the controller instance and the generic router name
__all__ = [
    'layout_controller',
    'router'
] 
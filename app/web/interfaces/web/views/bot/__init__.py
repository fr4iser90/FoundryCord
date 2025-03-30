from .bot_overview_view import router as bot_overview_router
from .bot_control_view import router as bot_control_router
from .bot_stats_view import router as bot_stats_router

__all__ = ['bot_overview_router', 'bot_control_router', 'bot_stats_router'] 
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import templates_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity, AppUserEntity
from sqlalchemy import select, func
from app.shared.interface.logging.api import get_web_logger
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = templates_extension()
logger = get_web_logger()

def datetime_filter(value):
    """Convert datetime object to string format"""
    if value is None:
        return "Never"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    return value.strftime("%Y-%m-%d %H:%M:%S")

class AdminView:
    """View für Admin-Bereich"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
        templates.env.filters["datetime"] = datetime_filter
    
    def _register_routes(self):
        """Register all routes for admin section"""
        self.router.get("", response_class=HTMLResponse)(self.index)
        self.router.get("/system", response_class=HTMLResponse)(self.system_status)
        self.router.get("/logs", response_class=HTMLResponse)(self.logs)

    async def index(self, request: Request):
        """Admin dashboard overview"""
        try:
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER", "ADMIN"]:
                return templates.TemplateResponse(
                    "views/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )
            
            admin_stats = {
                "guild_count": 0,
                "user_count": 0,
                "active_users": 0,
                "bot_uptime": "Unknown"
            }
            
            try:
                async with session_context() as session:
                    try:
                        guild_count = await session.execute(select(func.count(GuildEntity.id)))
                        admin_stats["guild_count"] = guild_count.scalar() or 0
                    except Exception as db_err:
                        logger.warning(f"Could not load guild statistics: {db_err}")
                    
                    try:
                        user_count = await session.execute(select(func.count(AppUserEntity.id)))
                        user_count_val = user_count.scalar() or 0
                        admin_stats["user_count"] = user_count_val
                        admin_stats["active_users"] = user_count_val
                    except Exception as db_err:
                        logger.warning(f"Could not load user statistics: {db_err}")
            except Exception as session_err:
                logger.warning(f"Could not establish database connection: {session_err}")
            
            return templates.TemplateResponse(
                "views/admin/index.html",
                {
                    "request": request, 
                    "user": user,
                    "stats": admin_stats,
                    "active_page": "admin-dashboard"
                }
            )
        except Exception as e:
            logger.error(f"Error in admin dashboard: {e}")
            return templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )
    
    async def system_status(self, request: Request):
        """System status and control panel"""
        try:
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER"]:
                return templates.TemplateResponse(
                    "views/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )
            
            import psutil
            import platform
            
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": f"{memory.used / (1024 * 1024 * 1024):.1f} GB",
                "memory_total": f"{memory.total / (1024 * 1024 * 1024):.1f} GB",
                "disk_percent": disk.percent,
                "disk_used": f"{disk.used / (1024 * 1024 * 1024):.1f} GB",
                "disk_total": f"{disk.total / (1024 * 1024 * 1024):.1f} GB",
            }
            
            return templates.TemplateResponse(
                "views/admin/system_status.html",
                {
                    "request": request, 
                    "user": user,
                    "system_info": system_info,
                    "active_page": "admin-system"
                }
            )
        except Exception as e:
            logger.error(f"Error in system status: {e}")
            return templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )

    async def logs(self, request: Request):
        """System and application logs"""
        try:
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER", "ADMIN"]:
                return templates.TemplateResponse(
                    "views/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )
            
            # Mock logs for now - will be replaced with actual log retrieval
            logs = [
                {
                    "id": 1,
                    "timestamp": "2024-03-10 12:34:56",
                    "level": "INFO",
                    "source": "System",
                    "message": "Application started",
                    "details": None
                },
                {
                    "id": 2,
                    "timestamp": "2024-03-10 12:35:01",
                    "level": "WARNING",
                    "source": "Bot",
                    "message": "High CPU usage detected",
                    "details": {"cpu_usage": "85%", "process_id": "1234"}
                },
                {
                    "id": 3,
                    "timestamp": "2024-03-10 12:36:15",
                    "level": "ERROR",
                    "source": "Web",
                    "message": "Database connection failed",
                    "details": {"error": "Connection timeout"}
                }
            ]
            
            return templates.TemplateResponse(
                "views/admin/logs.html",
                {
                    "request": request,
                    "user": user,
                    "logs": logs,
                    "active_page": "admin-logs"
                }
            )
        except Exception as e:
            logger.error(f"Error in logs view: {e}")
            return templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )

# View instance
admin_view = AdminView()
index = admin_view.index
system_status = admin_view.system_status
logs = admin_view.logs 
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import templates_extension
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity, AppUserEntity
from sqlalchemy import select, func
from app.shared.interface.logging.api import get_web_logger
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from datetime import datetime
from app.web.interfaces.web.views.base_view import BaseView

router = APIRouter(prefix="/admin", tags=["Admin"])

logger = get_web_logger()

class AdminView(BaseView):
    """View für Admin-Bereich"""
    
    def __init__(self):
        super().__init__(APIRouter(prefix="/admin", tags=["Admin"]))
        # Jetzt haben wir Zugriff auf self.templates
        self.templates.env.filters["datetime"] = self.datetime_filter
        self._register_routes()
    
    @staticmethod
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
    
    def _register_routes(self):
        """Register all routes for admin section"""
        self.router.get("", response_class=HTMLResponse)(self.index)
        self.router.get("/system", response_class=HTMLResponse)(self.system_status)
        self.router.get("/logs", response_class=HTMLResponse)(self.logs)

    async def index(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Admin dashboard overview"""
        try:
            if not await self.authz_service.check_permission(current_user, "VIEW_ADMIN_DASHBOARD"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
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
            
            return self.templates.TemplateResponse(
                "views/admin/index.html",
                {
                    "request": request, 
                    "user": current_user,
                    "stats": admin_stats,
                    "active_page": "admin-dashboard"
                }
            )
        except Exception as e:
            logger.error(f"Error in admin dashboard: {e}")
            return self.templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": current_user, "error": str(e)}
            )
    
    async def system_status(self, request: Request):
        """System status and control panel"""
        try:
            user = request.session.get("user")
            if not user or not user.is_owner:
                return self.templates.TemplateResponse(
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
            
            return self.templates.TemplateResponse(
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
            return self.templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )

    async def logs(self, request: Request):
        """System and application logs"""
        try:
            user = request.session.get("user")
            if not user or not any(role.name in ["OWNER", "ADMIN"] for role in user.guild_roles):
                return self.templates.TemplateResponse(
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
            
            return self.templates.TemplateResponse(
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
            return self.templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )

# Create services using factory
services = WebServiceFactory().create()
admin_view = AdminView()

# Export routes
index = admin_view.index
system_status = admin_view.system_status
logs = admin_view.logs 
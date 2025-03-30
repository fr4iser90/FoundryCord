from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity, AppUserEntity, DiscordGuildUserEntity
from sqlalchemy import select, func
from app.shared.interface.logging.api import get_web_logger
from app.shared.domain.auth.models import OWNER, ADMINS, MODERATORS, USERS, GUESTS
from app.shared.domain.auth.policies.authorization_policies import is_bot_owner

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = get_templates()
logger = get_web_logger()

class AdminView:
    """View für Admin-Bereich"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("", response_class=HTMLResponse)(self.admin_index)
        self.router.get("/dashboard", response_class=HTMLResponse)(self.admin_dashboard)
        self.router.get("/users", response_class=HTMLResponse)(self.user_management)
        self.router.get("/system", response_class=HTMLResponse)(self.system_status)
        #self.router.get("/bot-control", response_class=HTMLResponse)(self.bot_control)
        #self.router.get("/servers", response_class=HTMLResponse)(self.servers_management)           
        #self.router.get("/maintenance", response_class=HTMLResponse)(self.maintenance_management)     

    async def admin_index(self, request: Request):
        """Redirect to admin dashboard"""
        return RedirectResponse(url="/admin/dashboard")

    async def admin_dashboard(self, request: Request):
        """Admin dashboard overview"""
        try:
            # Session-basierte Autorisierung
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER"]:
                return templates.TemplateResponse(
                    "auth/insufficient_permissions.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )
            
            # Standardwerte für Statistiken
            admin_stats = {
                "guild_count": 0,
                "user_count": 0,
                "active_users": 0,
                "bot_uptime": "Unknown"
            }
            
            # Versuche, zusätzliche Daten aus der Datenbank zu laden, aber fange Fehler ab
            try:
                async with session_context() as session:
                    try:
                        # Versuche, Guild-Statistiken zu laden
                        guild_count = await session.execute(select(func.count(GuildEntity.id)))
                        admin_stats["guild_count"] = guild_count.scalar() or 0
                    except Exception as db_err:
                        logger.warning(f"Konnte Guild-Statistiken nicht laden: {db_err}")
                    
                    try:
                        # Versuche, User-Statistiken zu laden
                        user_count = await session.execute(select(func.count(AppUserEntity.id)))
                        user_count_val = user_count.scalar() or 0
                        admin_stats["user_count"] = user_count_val
                        admin_stats["active_users"] = user_count_val  # Vereinfachte Annahme
                    except Exception as db_err:
                        logger.warning(f"Konnte User-Statistiken nicht laden: {db_err}")
            except Exception as session_err:
                logger.warning(f"Konnte keine Datenbankverbindung herstellen: {session_err}")
            
            # Anzeige des Dashboards mit den verfügbaren Daten
            return templates.TemplateResponse(
                "pages/admin/dashboard.html",
                {
                    "request": request, 
                    "user": user,
                    "stats": admin_stats,
                    "active_page": "admin-dashboard"
                }
            )
        except Exception as e:
            logger.error(f"Error in admin dashboard: {e}")
            user = request.session.get("user")
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )
    
    async def user_management(self, request: Request):
        """User management page"""
        try:
            # Session-basierte Autorisierung
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER",]:
                return templates.TemplateResponse(
                    "pages/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )
            
            # URL-Parameter abrufen
            selected_server = request.query_params.get("server", "all")
            
            users = []
            servers = []
            
            try:
                async with session_context() as session:
                    # Verfügbare Server abrufen
                    # Nehmen wir an, wir haben eine Guild-Entität oder eine ähnliche Tabelle
                    # Passe dies entsprechend deiner tatsächlichen Modelle an
                    try:
                        guild_query = select(GuildEntity)
                        guild_result = await session.execute(guild_query)
                        db_guilds = guild_result.scalars().all()
                        
                        for guild in db_guilds:
                            servers.append({
                                "id": guild.id,
                                "name": guild.name
                            })
                    except Exception as guild_err:
                        logger.warning(f"Fehler beim Abrufen der Server: {guild_err}")
                        servers = []  # Fallback: leere Liste
                    
                    # Benutzer abrufen
                    query = select(AppUserEntity)
                    result = await session.execute(query)
                    db_users = result.scalars().all()
                    
                    for db_user in db_users:
                        # Grundlegende Benutzerinformationen
                        user_data = {
                            "id": db_user.id,
                            "username": db_user.username,
                            "discord_id": db_user.discord_id,
                            "role_id": db_user.role_id,  # Systemweite Rolle
                            "is_active": db_user.is_active,
                            "created_at": db_user.created_at,
                            "server_ids": [],  # Liste der Server-IDs, in denen dieser Benutzer ist
                            "server_roles": {}  # Server-spezifische Rollen
                        }
                        
                        # Server-spezifische Informationen abrufen
                        try:
                            # DiscordGuildUserEntity-Abfrage für diesen Benutzer
                            guild_user_query = select(DiscordGuildUserEntity).where(
                                DiscordGuildUserEntity.user_id == db_user.id
                            )
                            guild_user_result = await session.execute(guild_user_query)
                            guild_users = guild_user_result.scalars().all()
                            
                            for guild_user in guild_users:
                                user_data["server_ids"].append(guild_user.guild_id)
                                user_data["server_roles"][guild_user.guild_id] = guild_user.role_id
                        except Exception as guild_user_err:
                            logger.warning(f"Fehler beim Abrufen der Server-Benutzerinformationen: {guild_user_err}")
                        
                        users.append(user_data)
            except Exception as db_err:
                logger.error(f"Datenbankfehler beim Abrufen der Benutzer: {db_err}")
                users = []
                servers = []
            
            return templates.TemplateResponse(
                "pages/admin/user_management.html",
                {
                    "request": request, 
                    "user": user,
                    "users": users,
                    "servers": servers,
                    "selected_server": selected_server,
                    "active_page": "admin-users"
                }
            )
        except Exception as e:
            logger.error(f"Error in user management: {e}")
            user = request.session.get("user")
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )
    
    async def system_status(self, request: Request):
        """System status and logs"""
        try:
            # Session-basierte Autorisierung
            user = request.session.get("user")
            if not user or user.get("role") not in ["OWNER"]:
                return templates.TemplateResponse(
                    "pages/errors/403.html",
                    {"request": request, "user": user, "error": "Insufficient permissions"}
                )
            
            # Hier Systemstatistiken sammeln (z.B. mit psutil)
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
            
            # Mock-Logs (später durch echte Logs ersetzen)
            logs = [
                {"timestamp": "2025-03-10 12:34:56", "level": "INFO", "message": "Application started"},
                {"timestamp": "2025-03-10 12:35:01", "level": "INFO", "message": "User admin logged in"},
                {"timestamp": "2025-03-10 12:36:15", "level": "WARNING", "message": "High CPU usage detected"},
                {"timestamp": "2025-03-10 12:37:30", "level": "ERROR", "message": "Database connection failed temporarily"},
                {"timestamp": "2025-03-10 12:37:35", "level": "INFO", "message": "Database reconnected successfully"}
            ]
            
            return templates.TemplateResponse(
                "pages/admin/system_status.html",
                {
                    "request": request, 
                    "user": user,
                    "system_info": system_info,
                    "logs": logs,
                    "active_page": "admin-system"
                }
            )
        except Exception as e:
            logger.error(f"Error in system status: {e}")
            user = request.session.get("user")
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {"request": request, "user": user, "error": str(e)}
            )

# View-Instanz erzeugen
admin_view = AdminView()
admin_index = admin_view.admin_index
admin_dashboard = admin_view.admin_dashboard
user_management = admin_view.user_management
system_status = admin_view.system_status 
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.interfaces.api.rest.v1.bot.bot_admin_controller import get_overview_stats
import psutil
from app.web.domain.error.error_service import ErrorService
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/bot", tags=["Bot"])
logger = get_web_logger()
templates = get_templates()
error_service = ErrorService()

class BotOverviewView:
    """View für Bot-Übersicht"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/overview", response_class=HTMLResponse)(self.bot_overview)
    
    async def bot_overview(self, request: Request, current_user=Depends(get_current_user)):
        """Bot overview dashboard"""
        try:
            # Holen der Bot-Statistiken für das Dashboard
            stats = await get_overview_stats(current_user)
            
            # Erhalte Systeminformationen
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            system_info = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": f"{memory.used / (1024 * 1024 * 1024):.1f} GB",
                "memory_total": f"{memory.total / (1024 * 1024 * 1024):.1f} GB"
            }
            
            return templates.TemplateResponse(
                "pages/bot/overview.html",
                {
                    "request": request, 
                    "user": current_user,
                    "stats": stats,
                    "system_info": system_info,
                    "active_page": "bot-overview"
                }
            )
        except Exception as e:
            logger.error(f"Error in bot_overview: {str(e)}", exc_info=True)
            # Let the global exception handler handle it
            raise

# View-Instanz erzeugen
bot_overview_view = BotOverviewView()
bot_overview = bot_overview_view.bot_overview 
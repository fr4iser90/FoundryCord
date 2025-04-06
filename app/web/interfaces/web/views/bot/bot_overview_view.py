from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.interfaces.api.rest.v1.owner import get_overview_stats, get_bot_status
import psutil
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/bot", tags=["Bot"])
logger = get_web_logger()
templates = templates_extension()

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
            stats = await get_overview_stats(current_user)
            bot_status = await get_bot_status(current_user)
            
            # Get system info
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            return templates.TemplateResponse(
                "views/bot/overview.html",
                {
                    "request": request,
                    "user": current_user,
                    "stats": stats,
                    "bot_status": bot_status,
                    "system_info": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used": f"{memory.used / (1024 * 1024 * 1024):.1f} GB",
                        "memory_total": f"{memory.total / (1024 * 1024 * 1024):.1f} GB"
                    },
                    "active_page": "bot-overview"
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error loading bot overview: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load bot overview"
            )

# View-Instanz erzeugen
bot_overview_view = BotOverviewView()
bot_overview = bot_overview_view.bot_overview 
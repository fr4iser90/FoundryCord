from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.interfaces.api.rest.v1.owner import get_overview_stats
import psutil
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(tags=["Home"])
logger = get_web_logger()
templates = templates_extension()

class HomeOverviewView:
    """View für Home-Übersicht"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/home", response_class=HTMLResponse)(self.home_overview)

    async def home_overview(self, request: Request, current_user=Depends(get_current_user)):
        """Home overview"""
        stats = await get_overview_stats(current_user)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot statistics not found"
            )
        
        # Get system info
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return templates.TemplateResponse(
            "views/home/index.html",
            {
                "request": request,
                "user": current_user,
                "stats": stats,
                "system_info": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used": f"{memory.used / (1024 * 1024 * 1024):.1f} GB",
                    "memory_total": f"{memory.total / (1024 * 1024 * 1024):.1f} GB"
                },
                "active_page": "home-overview"
            }
        )

# View-Instanz erzeugen
home_overview_view = HomeOverviewView()
home_overview = home_overview_view.home_overview 
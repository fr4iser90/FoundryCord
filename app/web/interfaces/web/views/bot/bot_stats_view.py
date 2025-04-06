from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.interfaces.api.rest.v1.bot.bot_public_controller import (
    get_system_resources,
    get_recent_activities,
    get_popular_commands
)

router = APIRouter(prefix="/bot", tags=["Bot Stats"])
templates = templates_extension()

class BotStatsView:
    """View für Bot-Statistiken"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/stats", response_class=HTMLResponse)(self.bot_stats)
        self.router.get("/activity", response_class=HTMLResponse)(self.bot_activity)
        self.router.get("/commands", response_class=HTMLResponse)(self.bot_commands)
    
    async def bot_stats(self, request: Request, current_user=Depends(get_current_user)):
        """Bot statistics dashboard"""
        # Hole System-Ressourcen für die Statistiken
        system_resources = await get_system_resources()
        
        return templates.TemplateResponse(
            "views/bot/stats.html",
            {
                "request": request, 
                "user": current_user,
                "system_resources": system_resources,
                "active_page": "bot-stats"
            }
        )
    
    async def bot_activity(self, request: Request, current_user=Depends(get_current_user)):
        """Bot activity timeline"""
        # Hole kürzlich durchgeführte Aktivitäten
        activities = await get_recent_activities()
        
        return templates.TemplateResponse(
            "views/bot/activity.html",
            {
                "request": request, 
                "user": current_user,
                "activities": activities,
                "active_page": "bot-activity"
            }
        )
    
    async def bot_commands(self, request: Request, current_user=Depends(get_current_user)):
        """Bot command usage statistics"""
        # Hole beliebteste Befehle
        commands = await get_popular_commands()
        
        return templates.TemplateResponse(
            "views/bot/commands.html",
            {
                "request": request, 
                "user": current_user,
                "commands": commands,
                "active_page": "bot-commands"
            }
        )

# View-Instanz erzeugen
bot_stats_view = BotStatsView()
bot_stats = bot_stats_view.bot_stats
bot_activity = bot_stats_view.bot_activity
bot_commands = bot_stats_view.bot_commands 
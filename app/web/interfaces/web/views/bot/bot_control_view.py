from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role

router = APIRouter(prefix="/bot", tags=["Bot Control"])
templates = get_templates()

class BotControlView:
    """View für Bot-Steuerung"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/control", response_class=HTMLResponse)(self.bot_control)
    
    async def bot_control(self, request: Request, current_user=Depends(get_current_user)):
        """Bot control panel"""
        try:
            # Admin-Rolle prüfen
            await require_role(current_user, Role.OWNER)
            
            return templates.TemplateResponse(
                "pages/bot/control.html",
                {
                    "request": request, 
                    "user": current_user,
                    "active_page": "bot-control"
                }
            )
        except Exception as e:
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {"request": request, "user": current_user, "error": str(e)}
            )

# View-Instanz erzeugen
bot_control_view = BotControlView()
bot_control = bot_control_view.bot_control 
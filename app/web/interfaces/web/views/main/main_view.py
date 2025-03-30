from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import get_templates
from app.web.domain.error.error_service import ErrorService

router = APIRouter(tags=["Main"])
templates = get_templates()

class MainView:
    """View für Hauptseiten"""
    
    def __init__(self):
        self.router = router
        self.error_service = ErrorService()
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/", response_class=HTMLResponse)(self.index)
        self.router.get("/about", response_class=HTMLResponse)(self.about)
        self.router.get("/help", response_class=HTMLResponse)(self.help_page)
    
    async def index(self, request: Request):
        try:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "user": request.session.get("user")}
            )
        except Exception as e:
            return await self.error_service.handle_error(request, 500, str(e))
    
    async def about(self, request: Request):
        """About page"""
        return templates.TemplateResponse(
            "pages/about.html",
            {
                "request": request, 
                "user": request.session.get("user"),
                "active_page": "about"
            }
        )
    
    async def help_page(self, request: Request):
        """Help page"""
        return templates.TemplateResponse(
            "pages/help.html",
            {
                "request": request, 
                "user": request.session.get("user"),
                "active_page": "help"
            }
        )

# View-Instanz erzeugen
main_view = MainView()
home = main_view.index
about = main_view.about
help_page = main_view.help_page 
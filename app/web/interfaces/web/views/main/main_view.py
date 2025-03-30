from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import get_templates

router = APIRouter(tags=["Main"])
templates = get_templates()

class MainView:
    """View für Hauptseiten"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/", response_class=HTMLResponse)(self.home)
        self.router.get("/about", response_class=HTMLResponse)(self.about)
        self.router.get("/help", response_class=HTMLResponse)(self.help_page)
    
    async def home(self, request: Request):
        """Home page"""
        # Hier ist das Problem - dieses Template existiert nicht
        # Ändern zu "index.html", da dieses Template vorhanden ist
        return templates.TemplateResponse(
            "index.html",  # Korrigiert von "pages/home.html"
            {
                "request": request, 
                "user": request.session.get("user"),
                "active_page": "home"
            }
        )
    
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
home = main_view.home
about = main_view.about
help_page = main_view.help_page 
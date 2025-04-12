from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import templates_extension

router = APIRouter(tags=["Main"])


class MainView:
    """View für Hauptseiten"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/", response_class=HTMLResponse)(self.index)
        self.router.get("/about", response_class=HTMLResponse)(self.about)
        self.router.get("/help", response_class=HTMLResponse)(self.help_page)
    
    async def index(self, request: Request):
        try:
            return templates_extension().TemplateResponse(
                "views/main/index.html",
                {"request": request, "user": request.session.get("user")}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def about(self, request: Request):
        """About page"""
        return templates_extension().TemplateResponse(
            "views/main/about.html",
            {
                "request": request, 
                "user": request.session.get("user"),
                "active_page": "about"
            }
        )
    
    async def help_page(self, request: Request):
        """Help page"""
        return templates_extension().TemplateResponse(
            "views/main/help.html",
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
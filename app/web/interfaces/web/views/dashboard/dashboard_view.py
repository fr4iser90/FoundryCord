from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.interfaces.api.rest.v1.bot.bot_admin_controller import get_overview_stats
from app.web.interfaces.api.rest.v1.dashboard.dashboard_controller import get_layouts, get_layout
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(tags=["Dashboard"])
templates = get_templates()
logger = get_web_logger()

class DashboardView:
    """View für Dashboard-Funktionen"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diese View"""
        self.router.get("/dashboard", response_class=HTMLResponse)(self.dashboard)
        self.router.get("/dashboard/{layout_id}", response_class=HTMLResponse)(self.dashboard_with_layout)
        self.router.get("/dashboard/builder", response_class=HTMLResponse)(self.dashboard_builder)
        self.router.post("/dashboard/builder")(self.save_dashboard)
    
    async def dashboard(self, request: Request, current_user=Depends(get_current_user)):
        """Main user dashboard with default layout"""
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        try:
            # Bot-Statistiken für das Dashboard abrufen
            bot_stats = await get_overview_stats(current_user)
            
            # Verfügbare Dashboard-Layouts für den Nutzer abrufen
            layouts = await get_layouts(current_user)
            
            # Das Standard-Layout finden
            default_layout = next((l for l in layouts if l.get("is_default")), layouts[0] if layouts else None)
            
            if default_layout:
                # Wenn ein Layout vorhanden ist, leite zum spezifischen Layout weiter
                layout_id = default_layout.get("id")
                return RedirectResponse(
                    url=f"/dashboard/{layout_id}", 
                    status_code=status.HTTP_303_SEE_OTHER
                )
            
            # Fallback, wenn kein Layout gefunden wurde
            return templates.TemplateResponse(
                "pages/dashboard/empty.html",
                {
                    "request": request, 
                    "user": current_user,
                    "active_page": "dashboard"
                }
            )
        except Exception as e:
            logger.error(f"Error in dashboard: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {"request": request, "user": current_user, "error": str(e)}
            )
    
    async def dashboard_with_layout(self, layout_id: int, request: Request, current_user=Depends(get_current_user)):
        """Display dashboard with specific layout"""
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        try:
            # Layout-Daten abrufen
            layout = await get_layout(layout_id, current_user)
            
            # Verfügbare Layouts für die Navigation abrufen
            layouts = await get_layouts(current_user)
            
            # Bot-Statistiken für das Dashboard abrufen
            bot_stats = await get_overview_stats(current_user)
            
            return templates.TemplateResponse(
                "pages/dashboard/dashboard.html",
                {
                    "request": request, 
                    "user": current_user,
                    "layout": layout,
                    "available_layouts": layouts,
                    "stats": bot_stats,
                    "active_page": "dashboard"
                }
            )
        except HTTPException as he:
            if he.status_code == 404:
                return templates.TemplateResponse(
                    "pages/errors/404.html",
                    {"request": request, "user": current_user, "error": "Dashboard layout not found"}
                )
            raise
        except Exception as e:
            logger.error(f"Error in dashboard with layout: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {"request": request, "user": current_user, "error": str(e)}
            )
    
    async def dashboard_builder(self, request: Request, current_user=Depends(get_current_user)):
        """Dashboard builder interface"""
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        try:
            # Verfügbare Widgets für den Builder abrufen
            from app.web.interfaces.api.rest.v1.dashboard.dashboard_controller import get_available_widgets
            widgets = await get_available_widgets(current_user)
            
            # Existierende Layouts abrufen (falls der Nutzer ein Layout bearbeiten möchte)
            layouts = await get_layouts(current_user)
            
            return templates.TemplateResponse(
                "pages/dashboard/builder.html",
                {
                    "request": request, 
                    "user": current_user,
                    "widgets": widgets,
                    "layouts": layouts,
                    "active_page": "dashboard-builder"
                }
            )
        except Exception as e:
            logger.error(f"Error in dashboard builder: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {"request": request, "user": current_user, "error": str(e)}
            )
    
    async def save_dashboard(self, 
                            request: Request, 
                            layout_data: dict = Form(...),
                            current_user=Depends(get_current_user)):
        """Save dashboard layout"""
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        try:
            # Layout speichern
            from app.web.interfaces.api.rest.v1.dashboard.dashboard_controller import create_layout, update_layout
            
            if "id" in layout_data and layout_data["id"]:
                # Bestehendes Layout aktualisieren
                layout_id = layout_data["id"]
                layout = await update_layout(layout_id, layout_data, current_user)
            else:
                # Neues Layout erstellen
                layout = await create_layout(layout_data, current_user)
                layout_id = layout["id"]
            
            # Weiterleitung zum Dashboard mit dem gespeicherten Layout
            return RedirectResponse(
                url=f"/dashboard/{layout_id}", 
                status_code=status.HTTP_303_SEE_OTHER
            )
        except Exception as e:
            logger.error(f"Error saving dashboard: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {"request": request, "user": current_user, "error": str(e)}
            )

# View-Instanz erzeugen
dashboard_view = DashboardView()
dashboard = dashboard_view.dashboard
dashboard_with_layout = dashboard_view.dashboard_with_layout
dashboard_builder = dashboard_view.dashboard_builder
save_dashboard = dashboard_view.save_dashboard 
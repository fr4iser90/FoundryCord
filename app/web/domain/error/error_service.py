from fastapi import Request, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()
templates = get_templates()

class ErrorService:
    """Service für Error-Handling Logik"""
    
    ERROR_TEMPLATES = {
        400: "pages/errors/400.html",
        401: "pages/errors/401.html",
        403: "pages/errors/403.html",
        404: "pages/errors/404.html",
        500: "pages/errors/500.html",
        503: "pages/errors/503.html"
    }
    
    ERROR_MESSAGES = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
        503: "Service Unavailable"
    }
    
    async def handle_error(
        self, 
        request: Request, 
        status_code: int, 
        error_message: str = None
    ) -> HTMLResponse:
        """Verarbeitet Fehler und rendert Error-Page"""
        logger.error(f"Error {status_code}: {error_message}")
        
        template = self.ERROR_TEMPLATES.get(
            status_code, 
            "pages/errors/500.html"
        )
        
        if not error_message:
            error_message = self.ERROR_MESSAGES.get(
                status_code,
                "An unknown error occurred"
            )
            
        return templates.TemplateResponse(
            template,
            {
                "request": request,
                "user": request.session.get("user"),
                "error": error_message
            },
            status_code=status_code
        ) 
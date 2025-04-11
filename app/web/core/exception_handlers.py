from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from app.web.interfaces.web.views.base_view import BaseView
import logging # Import standard logging
import uuid
from typing import Dict, Any

# Use standard logger directly for exception handling
base_logger = logging.getLogger("homelab.bot.exceptions") # More specific logger name

class ErrorHandler(BaseView):
    def __init__(self):
        super().__init__(None)  # No router needed for Error Handler
        # Keep self.logger for potential non-exception logging if needed elsewhere
        # from app.shared.interface.logging.api import get_web_logger
        # self.logger = get_web_logger()

    def _build_error_context(self, request: Request, exc: Exception) -> Dict[str, Any]:
        """Build structured context for error logging"""
        return {
            'request_id': str(uuid.uuid4()),
            'path': request.url.path,
            'method': request.method,
            'client_host': request.client.host if request.client else "unknown",
            'user_id': request.session.get("user", {}).get("id", "anonymous"),
            'error_type': exc.__class__.__name__,
            # 'error_detail': str(exc) # Detail comes from the exception message itself when logged
        }

    async def handle_http_exception(self, request: Request, exc: HTTPException):
        """Enhanced HTTP exception handler with unified logging"""
        context = self._build_error_context(request, exc)
        is_api_path = request.url.path.startswith("/api/")
        error_message = f"HTTP {exc.status_code} for {request.method} {request.url.path}: {exc.detail}"
        
        if exc.status_code >= 500:
            # Log 5xx errors with full exception info and context
            base_logger.exception(error_message, exc_info=exc, extra=context) 
        else:
            # Log 4xx client errors as warnings with context, no traceback needed
            base_logger.warning(error_message, extra=context)
        
        if is_api_path:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": str(exc.detail),
                    "request_id": context['request_id']
                }
            )
        
        # Pass context for rendering, ensure request_id is available
        render_context = {
            "request": request, 
            "error": str(exc.detail),
            "status_code": exc.status_code,
            "request_id": context.get('request_id', 'N/A')
        }
        
        # Correct path to error templates: views/errors/
        template_path = f"views/errors/{exc.status_code}.html"
        
        try:
            return self.templates.TemplateResponse(template_path, render_context)
        except Exception as render_exc: 
            # Log rendering error separately
            base_logger.exception(f"Failed to render template {template_path}", exc_info=render_exc)
            # Fallback to generic 500
            render_context["error"] = "Internal server error (template rendering failed)"
            render_context["status_code"] = 500
            return self.templates.TemplateResponse("views/errors/500.html", render_context)

    async def handle_generic_exception(self, request: Request, exc: Exception):
        """Enhanced generic exception handler with unified logging"""
        context = self._build_error_context(request, exc)
        is_api_path = request.url.path.startswith("/api/")
        error_message = f"Unhandled Exception for {request.method} {request.url.path}: {str(exc)}"

        # Log unhandled exceptions with full exception info and context
        base_logger.exception(error_message, exc_info=exc, extra=context)
        
        if is_api_path:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": context.get('request_id', 'N/A')
                }
            )
        
        # Pass context for rendering, ensure request_id is available
        render_context = {
            "request": request,
            "error": "Internal server error",
            "status_code": 500,
            "request_id": context.get('request_id', 'N/A')
        }
        
        # Correct path to 500 error template: views/errors/
        template_path = "views/errors/500.html"
        
        try:
            return self.templates.TemplateResponse(template_path, render_context)
        except Exception as render_exc:
            base_logger.exception(f"Failed to render template {template_path}", exc_info=render_exc)
            # Ultimate fallback if even 500.html fails (rare)
            return JSONResponse(
                 status_code=500,
                 content={"detail": "Critical internal server error", "request_id": context.get('request_id', 'N/A')}
             )

# Create singleton instance
error_handler = ErrorHandler()

# Export handler functions
http_exception_handler = error_handler.handle_http_exception
generic_exception_handler = error_handler.handle_generic_exception

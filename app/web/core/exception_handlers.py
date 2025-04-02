from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from app.web.core.extensions import get_templates
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

async def http_exception_handler(request: Request, exc: HTTPException):
    """Unified HTTP exception handler"""
    path = request.url.path
    is_api_path = path.startswith("/api/")
    
    # Log the error
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} error at {path}: {exc.detail}", exc_info=True)
    else:
        logger.warning(f"HTTP {exc.status_code} error at {path}: {exc.detail}")
    
    # Handle API requests
    if is_api_path:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail)}
        )
    
    # Handle web requests
    try:
        templates = get_templates()
        template_path = f"pages/errors/{exc.status_code}.html"
        
        context = {
            "request": request,
            "error": str(exc.detail),
            "user": request.session.get("user"),
            "status_code": exc.status_code
        }
        
        return templates.TemplateResponse(
            template_path,
            context,
            status_code=exc.status_code
        )
    except Exception as e:
        logger.error(f"Error rendering error template: {e}", exc_info=True)
        # Fallback to basic error response
        return HTMLResponse(
            content=f"Error {exc.status_code}: {exc.detail}",
            status_code=exc.status_code
        )

async def generic_exception_handler(request: Request, exc: Exception):
    """Unified generic exception handler"""
    path = request.url.path
    is_api_path = path.startswith("/api/")
    
    # Always log the full exception for 500 errors
    logger.error(f"Unhandled exception at {path}", exc_info=True)
    
    if is_api_path:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    try:
        templates = get_templates()
        return templates.TemplateResponse(
            "pages/errors/500.html",
            {
                "request": request,
                "error": str(exc) if app.debug else "An unexpected error occurred",
                "user": request.session.get("user"),
                "status_code": 500
            },
            status_code=500
        )
    except Exception as e:
        logger.error(f"Error rendering 500 template: {e}", exc_info=True)
        return HTMLResponse(
            content="Internal Server Error",
            status_code=500
        )

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from app.web.core.extensions import templates_extension
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

async def http_exception_handler(request: Request, exc: HTTPException):
    """Unified HTTP exception handler"""
    path = request.url.path
    is_api_path = path.startswith("/api/")
    
    # Log the error
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} error at {path}: {exc.detail}")
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
        templates = templates_extension()
        template_path = f"views/errors/{exc.status_code}.html"
        
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
        logger.error(f"Error rendering error template: {e}")
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
    logger.error(f"Unhandled exception at {path}")
    
    if is_api_path:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    try:
        templates = templates_extension()
        return templates.TemplateResponse(
            "views/errors/500.html",
            {
                "request": request,
                "error": str(exc),
                "user": request.session.get("user"),
                "status_code": 500
            },
            status_code=500
        )
    except Exception as e:
        logger.error(f"Error rendering 500 template: {e}")
        return HTMLResponse(
            content="Internal Server Error",
            status_code=500
        )

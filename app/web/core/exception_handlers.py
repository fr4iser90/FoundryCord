from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from app.web.domain.error.error_service import ErrorService
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()
error_service = ErrorService()

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPExceptions by rendering appropriate error pages"""
    logger.info(f"HTTP exception handler called: {exc.status_code} - {exc.detail}")
    
    # Check if this is an API request or browser request
    path = request.url.path
    is_api_path = path.startswith("/api/")
    accepts_html = "text/html" in request.headers.get("accept", "")
    
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Is API path: {is_api_path}, Accepts HTML: {accepts_html}")
    
    if is_api_path or not accepts_html:
        logger.info(f"Returning JSON response for {exc.status_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # For web routes, use our error service to render HTML pages
    logger.info(f"Rendering HTML error {exc.status_code} page")
    return await error_service.handle_error(
        request=request,
        status_code=exc.status_code,
        error_message=str(exc.detail)
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with a 500 error page"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Check if this is an API request
    path = request.url.path
    is_api_path = path.startswith("/api/")
    accepts_html = "text/html" in request.headers.get("accept", "")
    
    if is_api_path or not accepts_html:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    return await error_service.handle_error(
        request=request,
        status_code=500,
        error_message="An unexpected error occurred"
    )
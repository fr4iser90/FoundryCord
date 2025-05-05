from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.interfaces.logging.api import get_web_logger
import uuid

logger = get_web_logger()

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and context logging."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # Store request ID in state for access in other parts of the application
        request.state.request_id = request_id 
        
        client_host = request.client.host if request.client else "unknown"
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'client_host': client_host
            }
        )
        
        try:
            response = await call_next(request)
            logger.info(
                f"Request completed: {request.method} {request.url.path} -> {response.status_code}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'client_host': client_host,
                    'status_code': response.status_code
                }
            )
            return response
        except Exception as e:
            # Log the exception with context
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=e, # Log exception info
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'client_host': client_host,
                    'error_type': e.__class__.__name__
                }
            )
            # Re-raise the exception so it can be handled by global exception handlers
            raise e 
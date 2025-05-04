from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from .base_logging_service import BaseLoggingService

class WebLoggingService(BaseLoggingService):
    """Logging service for the web application"""
    
    def __init__(self, app: FastAPI):
        super().__init__("homelab.web")
        self.app = app
    
    def setup_request_logging(self):
        """Set up request logging middleware"""
        self.app.add_middleware(BaseHTTPMiddleware, dispatch=self.log_request_info)
    
    async def log_request_info(self, request: Request, call_next):
        """Log the request information"""
        self.debug(f"Processing request: {request.method} {request.url.path}",
                 method=request.method, path=request.url.path)
        
        self.info(f"Web request: {request.method} {request.url.path}",
                 method=request.method, path=request.url.path, 
                 client=request.client.host if request.client else "unknown")
        
        response = await call_next(request)
        
        self.info(f"Response: {response.status_code}",
                status_code=response.status_code)
        return response 

    # Add explicit delegate method for clarity
    def critical(self, message, exception=None, **context):
        return super().critical(message, exception=exception, **context) 
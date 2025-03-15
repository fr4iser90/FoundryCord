# app/shared/logging/web_logging_service.py
import logging
# These imports will only be used when the web service is explicitly requested
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

# Import the logger
from .logger import web_logger

class WebLoggingService:
    def __init__(self, app: FastAPI):
        self.app = app

    def setup_request_logging(self):
        """Set up request logging middleware for the FastAPI application"""
        self.app.add_middleware(BaseHTTPMiddleware, dispatch=self.log_request_info)

    async def log_request_info(self, request: Request, call_next):
        """Log the request information before the request is processed"""
        web_logger.info(f"Web request: {request.method} {request.url.path} from {request.client.host}")
        response = await call_next(request)
        web_logger.info(f"Response: {response.status_code}")
        return response

    def log_error(self, error: Exception):
        """Log web application errors"""
        web_logger.error(f"Web error: {str(error)}")

# Remove the example usage so it's not executed on import
# app = FastAPI()
# logging_service = WebLoggingService(app)
# logging_service.setup_request_logging()
# @app.get("/")
# async def read_root():
#     return {"message": "Hello World"}
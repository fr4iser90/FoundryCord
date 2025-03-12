from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import os
import logging
from datetime import datetime, timedelta

from .config import Settings
from .routes import auth, user
from .services.auth_service import AuthService

# Load configuration
settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("web_interface")

# Initialize FastAPI app
app = FastAPI(
    title="HomeLab Discord Bot Web Interface",
    description="Web interface for managing the HomeLab Discord Bot",
    version="0.1.0",
)

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/bot/interfaces/web/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(user.router, prefix="/user", tags=["user"])

# Define dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def root(request: Request):
    """
    Root endpoint that redirects to login if not authenticated or dashboard if authenticated
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    """
    Main dashboard page, requires authentication
    """
    # This is a placeholder - proper authentication will be implemented
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests
    """
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info(f"Request: {request.method} {request.url.path} - {process_time:.2f}ms")
    return response

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions
    """
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "detail": "Internal Server Error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 
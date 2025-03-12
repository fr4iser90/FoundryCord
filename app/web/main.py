"""
Main application file for the HomeLab Discord Bot web interface.
"""
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import the bot modules through our bridge module
try:
    from bot_imports import get_bot_interfaces, BOT_IMPORTS_SUCCESS
    bot_interface = get_bot_interfaces()
except ImportError:
    bot_interface = None
    print("Warning: Bot interfaces not available. Some features will be disabled.")

# Create FastAPI application
app = FastAPI(
    title="HomeLab Discord Bot Web Interface",
    description="Web interface for managing the HomeLab Discord Bot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "HomeLab Discord Bot Web Interface is running",
        "bot_interface_available": bot_interface is not None
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot_interface": "available" if bot_interface is not None else "unavailable"
    }

# Debug endpoint to show Python path and available modules
@app.get("/debug")
async def debug():
    return {
        "python_path": sys.path,
        "bot_interface_available": bot_interface is not None,
        "current_directory": os.getcwd(),
        "directory_contents": os.listdir("/app") if os.path.exists("/app") else "Not available",
        "app_directory_exists": os.path.exists("/app/app"),
        "app_bot_directory_exists": os.path.exists("/app/app/bot"),
        "bot_directory_exists": os.path.exists("/app/bot")
    }

# Add error handler for graceful error messages
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)}
    ) 
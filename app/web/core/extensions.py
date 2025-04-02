"""
Extensions for the web application.
This module contains extensions that can be registered with the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from app.shared.interface.logging.api import get_web_logger
from datetime import datetime

logger = get_web_logger()

# Templates - initialized later
_templates = None

def init_templates(app: FastAPI):
    """Initialize Jinja2 templates"""
    global _templates
    
    web_dir = Path(__file__).parent.parent
    templates_dir = web_dir / "templates"
    
    logger.info(f"Initializing templates from directory: {templates_dir}")
    
    if not templates_dir.exists():
        logger.error(f"Templates directory not found: {templates_dir}")
        raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
    
    # Verify error templates exist
    error_templates_dir = templates_dir / "pages" / "errors"
    if not error_templates_dir.exists():
        logger.error(f"Error templates directory not found: {error_templates_dir}")
        raise FileNotFoundError(f"Error templates directory not found: {error_templates_dir}")
    
    # Check for required error templates
    required_error_templates = ['400.html', '401.html', '403.html', '404.html', '500.html', '503.html']
    for template in required_error_templates:
        template_path = error_templates_dir / template
        if not template_path.exists():
            logger.error(f"Required error template not found: {template_path}")
            raise FileNotFoundError(f"Required error template not found: {template_path}")
    
    _templates = Jinja2Templates(directory=str(templates_dir))
    _templates.env.filters['formatTimeAgo'] = format_time_ago
    
    return _templates

def init_static_files(app: FastAPI):
    """Initialize static files"""
    web_dir = Path(__file__).parent.parent
    static_dir = web_dir / "static"
    
    logger.info(f"Static directory absolute path: {static_dir.absolute()}")
    logger.info(f"Static directory exists: {static_dir.exists()}")
    
    if static_dir.exists():
        logger.info(f"Static directory contents: {list(static_dir.glob('**/*'))}")
    
    if not static_dir.exists():
        logger.error(f"Static directory not found: {static_dir}")
        raise FileNotFoundError(f"Static directory not found: {static_dir}")
    
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

def verify_static_paths(app: FastAPI):
    """Verify and log static file paths"""
    web_dir = Path(__file__).parent.parent
    static_dir = web_dir / "static"
    
    # Überprüfe und logge die wichtigsten Pfade
    css_base = static_dir / "css" / "base.css"
    css_theme = static_dir / "css" / "themes" / "dark" / "theme.css"
    js_main = static_dir / "js" / "main.js"
    
    logger.info(f"Checking static paths:")
    logger.info(f"base.css exists: {css_base.exists()}")
    logger.info(f"theme.css exists: {css_theme.exists()}")
    logger.info(f"main.js exists: {js_main.exists()}")
    
    # Füge die Funktion in init_all_extensions ein
    return {
        "css_base": css_base.exists(),
        "css_theme": css_theme.exists(), 
        "js_main": js_main.exists()
    }

def init_all_extensions(app: FastAPI):
    """Initialize all extensions"""
    global _templates
    _templates = init_templates(app)
    init_static_files(app)
    verify_static_paths(app)
    return _templates

def get_templates() -> Jinja2Templates:
    """Get configured Jinja2 templates instance"""
    global _templates
    
    if _templates is None:
        # Instead of warning, initialize properly
        web_dir = Path(__file__).parent.parent
        templates_dir = web_dir / "templates"
        
        if not templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
            
        _templates = Jinja2Templates(directory=str(templates_dir))
        _templates.env.filters['formatTimeAgo'] = format_time_ago
        logger.info("Templates initialized successfully")
        
    return _templates

def format_time_ago(timestamp):
    """Convert timestamp to "time ago" format"""
    # Ensure timestamp is a datetime object
    if isinstance(timestamp, str):
        # Parse the ISO format string to a datetime object
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            # If standard parsing fails, try a more flexible approach
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    
    # Get current time
    now = datetime.now()
    
    # Make both timestamps timezone-naive if timestamp has timezone info
    if timestamp.tzinfo is not None:
        # Convert to UTC and remove timezone info
        timestamp = timestamp.replace(tzinfo=None)
    
    # Calculate time difference
    diff = now - timestamp
    seconds = diff.total_seconds()
    
    # Format the time difference
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"

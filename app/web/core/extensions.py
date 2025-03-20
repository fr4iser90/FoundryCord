"""
Extensions for the web application.
This module contains extensions that can be registered with the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

# Templates - initialized later
_templates = None

def init_templates(app: FastAPI):
    """Initialize Jinja2 templates"""
    global _templates
    
    # Der Pfad war falsch - wir müssen zum web/templates Verzeichnis
    web_dir = Path(__file__).parent.parent
    templates_dir = web_dir / "templates"
    
    logger.info(f"Initializing templates from directory: {templates_dir}")
    logger.debug(f"Template directory contents: {os.listdir(templates_dir) if templates_dir.exists() else 'Directory not found'}")
    
    if not templates_dir.exists():
        logger.error(f"Templates directory not found: {templates_dir}")
        raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
    
    _templates = Jinja2Templates(directory=str(templates_dir))
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

def init_all_extensions(app: FastAPI):
    """Initialize all extensions"""
    global _templates
    _templates = init_templates(app)
    init_static_files(app)
    return _templates

def get_templates() -> Jinja2Templates:
    """Get configured Jinja2 templates instance"""
    global _templates
    if _templates is None:
        web_dir = Path(__file__).parent.parent
        templates_dir = web_dir / "templates"
        if not templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        _templates = Jinja2Templates(directory=str(templates_dir))
    return _templates

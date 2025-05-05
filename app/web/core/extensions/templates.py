"""
Templates extension module for handling Jinja2 templates and filters.
"""
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Dict, Optional
import logging
from .time import time_extension

logger = logging.getLogger(__name__)

class TemplatesExtension:
    def __init__(self):
        self._templates: Optional[Jinja2Templates] = None
        self._templates_dir: Optional[Path] = None
        self._initialized = False
        
    def __call__(self):
        """Make the extension callable to maintain compatibility with existing views"""
        if not self._initialized:
            # Default to web/templates directory if not initialized
            self._templates_dir = Path(__file__).parent.parent.parent / "templates"
            self._initialize_templates()
        return self._templates
        
    def init_app(self, app: FastAPI, templates_dir: Path = None):
        """Initialize templates for the application"""
        if templates_dir:
            self._templates_dir = templates_dir
        else:
            # Default to web/templates directory
            self._templates_dir = Path(__file__).parent.parent.parent / "templates"
            
        logger.debug(f"Templates directory: {self._templates_dir}")
        
        self._initialize_templates()
        
        # Store in app state for easy access
        app.state.templates = self._templates
        
        logger.info("Templates initialized successfully")
        
    def _initialize_templates(self):
        """Initialize the templates if not already done"""
        if self._initialized:
            return
            
        if not self._templates_dir.exists():
            logger.error(f"Templates directory not found: {self._templates_dir}")
            raise FileNotFoundError(f"Templates directory not found: {self._templates_dir}")
            
        # Verify error templates
        self._verify_error_templates()
        
        # Initialize Jinja2Templates
        self._templates = Jinja2Templates(directory=str(self._templates_dir))
        
        # Register filters
        self._register_filters()
        
        self._initialized = True
        
    def _verify_error_templates(self):
        """Verify that all required error templates exist"""
        error_dir = self._templates_dir / "views" / "errors"
        if not error_dir.exists():
            logger.error(f"Error templates directory not found: {error_dir}")
            raise FileNotFoundError(f"Error templates directory not found: {error_dir}")
            
        required_templates = ['400.html', '401.html', '403.html', '404.html', '500.html', '503.html']
        
        for template in required_templates:
            path = error_dir / template
            if not path.exists():
                logger.error(f"Required error template not found: {path}")
                raise FileNotFoundError(f"Required error template not found: {path}")
                
        #logger.debug("All required error templates verified")
        
    def _register_filters(self):
        """Register Jinja2 template filters"""
        if not self._templates:
            raise RuntimeError("Templates not initialized")
            
        # Time formatting filters
        self._templates.env.filters['formatTimeAgo'] = time_extension.format_time
        self._templates.env.filters['timeago'] = time_extension.format_time
        self._templates.env.filters['formatTime'] = lambda x: time_extension.format_time(x, use_time_ago=False)
        
        # Add more filters here as needed
        
    def get_template(self, name: str):
        """Get a template by name"""
        if not self._initialized:
            self._initialize_templates()
        return self._templates.get_template(name)
        
    @property
    def env(self):
        """Get the Jinja2 environment for direct access to filters etc."""
        if not self._initialized:
            self._initialize_templates()
        return self._templates.env
        
    @property
    def templates_dir(self) -> Path:
        """Get the templates directory"""
        return self._templates_dir

    def TemplateResponse(self, *args, **kwargs):
        """Proxy method to maintain compatibility with existing views"""
        if not self._initialized:
            self._initialize_templates()
        return self._templates.TemplateResponse(*args, **kwargs)

# Global instance
templates_extension = TemplatesExtension() 
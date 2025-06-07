"""
Extensions module for the web application.
Provides various extensions and utilities.
"""
from fastapi import FastAPI
from .time import time_extension
from .static import static_extension
from .templates import templates_extension

__all__ = [
    'time_extension',
    'static_extension',
    'templates_extension',
    'init_extensions'
]

def init_extensions(app: FastAPI):
    """Initialize all extensions for the application"""
    # Initialize static files first
    static_extension.init_app(app)
    
    # Initialize templates
    templates_extension.init_app(app)
    
    # Time extension doesn't need initialization
    
    return {
        'static': static_extension,
        'templates': templates_extension,
        'time': time_extension,
    } 
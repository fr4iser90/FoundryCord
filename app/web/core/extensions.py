"""
Extensions for the web application.
This module contains extensions that can be registered with the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Templates - initialized later
templates = None

def init_templates(app: FastAPI, directory: str = "app/web/templates"):
    """Initialize Jinja2 templates"""
    global templates
    
    # Make sure the templates directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Create and configure templates
    templates = Jinja2Templates(directory=directory)
    
    return templates

def init_static_files(app: FastAPI, directory: str = "app/web/static", mount_path: str = "/static"):
    """Initialize static files"""
    # Make sure the static directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Mount static files
    app.mount(mount_path, StaticFiles(directory=directory), name="static")

def init_all_extensions(app: FastAPI):
    """Initialize all extensions"""
    # Initialize templates first and save the reference
    global templates
    templates = init_templates(app)
    
    # Initialize static files
    init_static_files(app)
    
    return templates

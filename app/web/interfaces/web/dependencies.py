import os
import pathlib
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.web.domain.auth.dependencies import get_current_user

# Zentrale Template-Konfiguration
base_dir = pathlib.Path(__file__).parent.parent.parent
templates_dir = os.path.join(base_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

def get_templates():
    return templates

async def render_template(
    request: Request,
    template_name: str,
    **context
) -> HTMLResponse:
    """Helper function to render templates with common context"""
    return templates.TemplateResponse(
        template_name,
        {"request": request, **context}
    )

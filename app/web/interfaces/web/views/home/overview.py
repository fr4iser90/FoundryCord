from fastapi import Request, Depends, APIRouter
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
import psutil
from app.shared.interfaces.logging.api import get_web_logger
from app.web.infrastructure.extensions import templates_extension
router = APIRouter()
logger = get_web_logger()

@router.get("/home")
async def home_overview(request: Request, current_user: AppUserEntity = Depends(get_current_user)):
    """Renders the main home overview page with placeholder data."""
    # Import templates extension locally
    
    # Provide default placeholder data for template rendering
    # Actual data will be fetched by JavaScript API calls
    context = {
        "request": request,
        "user": current_user,
        "active_page": "home-overview",
        "stats": { # Placeholder for stats expected by template
            "server_count": "N/A",
            "member_count": "N/A",
            "active_tasks": "N/A"
        },
        "system_info": { # Placeholder for system info
            "cpu_percent": "N/A",
            "memory_percent": "N/A",
            "memory_used": "N/A",
            "memory_total": "N/A"
        },
        "recent_activities": [] # Placeholder for activities list
    }
    
    return templates_extension().TemplateResponse(
        "views/home/index.html", 
        context
    )

# Removed the old class structure if it existed 
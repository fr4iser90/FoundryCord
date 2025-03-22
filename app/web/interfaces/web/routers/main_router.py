from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root page with user context"""
    try:
        templates = get_templates()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": request.session.get("user") if hasattr(request, "session") else None,
                "dashboards": []  # We'll populate this later
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include all routers
from .auth_router import router as auth_router
from .dashboard_router import router as dashboard_router
from .admin_router import router as admin_router
from .bot_router import router as bot_router

router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(admin_router)
router.include_router(bot_router)

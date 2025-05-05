import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
# Corrected imports for middleware classes within the registry context
from app.web.core.middleware.request_tracking import RequestTrackingMiddleware 
from app.web.core.middleware.authentication import AuthenticationMiddleware
from app.shared.infrastructure.security import get_security_bootstrapper

logger = logging.getLogger(__name__)

def register_core_middleware(app: FastAPI):
    """Registers all core middleware in the correct order."""
    
    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Adjust as needed for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. Session Middleware
    try:
        security_bootstrapper = get_security_bootstrapper()
        session_secret = security_bootstrapper.get_key('JWT_SECRET_KEY')
        
        if not session_secret:
            logger.critical("CRITICAL: JWT_SECRET_KEY not found in SecurityBootstrapper during middleware setup!")
            raise RuntimeError("Failed to retrieve JWT_SECRET_KEY for session middleware.")
            
    except Exception as e:
        logger.critical(f"CRITICAL: Failed to get JWT_SECRET_KEY from SecurityBootstrapper: {e}", exc_info=True)
        raise RuntimeError("Could not configure session middleware due to missing security key.") from e

    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret, 
        session_cookie="homelab_session", 
        max_age=7 * 24 * 60 * 60,  # 1 week
        same_site="lax",
        https_only=os.getenv("ENVIRONMENT", "development").lower() != "development"
    )
    
    # 3. Authentication Middleware
    app.add_middleware(AuthenticationMiddleware)
    
    # 4. Request Tracking Middleware
    app.add_middleware(RequestTrackingMiddleware)

    logger.debug("Core middleware registered successfully via Middleware Registry.")

__all__ = ["register_core_middleware"] 
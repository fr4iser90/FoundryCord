"""
Central middleware configuration for the application.
This module handles all middleware setup in a clean, organized way.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.web.infrastructure.middleware.authentication import AuthenticationMiddleware
from app.web.infrastructure.middleware.request_tracking import RequestTrackingMiddleware
from app.web.infrastructure.middleware.session import SessionMiddleware
from app.shared.infrastructure.security import get_security_bootstrapper
import os
import logging

logger = logging.getLogger(__name__)

def setup_middleware(app: FastAPI) -> None:
    """
    Setup all middleware for the application in the correct order.
    This is the single source of truth for middleware configuration.
    """
    try:
        security_bootstrapper = get_security_bootstrapper()
        session_secret = security_bootstrapper.get_key('JWT_SECRET_KEY')
        
        if not session_secret:
            logger.critical("CRITICAL: JWT_SECRET_KEY not found in SecurityBootstrapper!")
            raise RuntimeError("Failed to retrieve JWT_SECRET_KEY for session middleware.")
            
        # 1. Request Tracking Middleware (first to track all requests)
        app.add_middleware(RequestTrackingMiddleware)
        
        # 2. CORS Middleware (before session/auth to handle preflight requests)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure this appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 3. Authentication Middleware (before session to check auth)
        app.add_middleware(AuthenticationMiddleware)
        
        # 4. Session Middleware (after auth to set session data)
        app.add_middleware(
            SessionMiddleware,
            secret_key=session_secret,
            session_cookie="homelab_session",
            max_age=7 * 24 * 60 * 60,  # 1 week
            same_site="lax",
            https_only=os.getenv("ENVIRONMENT", "development").lower() != "development"
        )
        
        logger.info("All middleware installed successfully")
            
    except Exception as e:
        logger.critical(f"CRITICAL: Failed to setup middleware: {e}", exc_info=True)
        raise RuntimeError("Could not configure middleware.") from e 
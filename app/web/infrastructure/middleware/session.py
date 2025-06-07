"""
Session middleware module for handling session management.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import jwt
import json
from typing import Dict, Any, Optional
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        secret_key: str,
        session_cookie: str = "session",
        max_age: int = 14 * 24 * 60 * 60,  # 14 days in seconds
        same_site: str = "lax",
        https_only: bool = False
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.same_site = same_site
        self.https_only = https_only

    async def dispatch(self, request: Request, call_next):
        # Get session data from cookie
        session_data = self._get_session(request)
        logger.debug(f"Retrieved session data from cookie: {session_data}")
        
        # Set session data in request scope
        request.scope["session"] = session_data if session_data else {}
        logger.debug(f"Set session data in request scope: {request.scope['session']}")
        
        # Process the request
        response = await call_next(request)
        
        # Always update session cookie if session data exists
        if "session" in request.scope and request.scope["session"]:
            logger.debug(f"Setting session cookie with data: {request.scope['session']}")
            self._set_session_cookie(response, request.scope["session"])
            
        return response

    def _get_session(self, request: Request) -> Dict[str, Any]:
        session_data = {}
        session_cookie = request.cookies.get(self.session_cookie)
        
        if session_cookie:
            try:
                session_data = jwt.decode(
                    session_cookie,
                    self.secret_key,
                    algorithms=["HS256"]
                )
                logger.debug(f"Successfully decoded session data: {session_data}")
            except jwt.InvalidTokenError:
                logger.warning("Invalid session token")
                session_data = {}
                
        return session_data

    def _set_session_cookie(self, response: Response, session_data: Dict[str, Any]):
        if not session_data:
            return

        try:
            encoded = jwt.encode(
                session_data,
                self.secret_key,
                algorithm="HS256"
            )
            
            response.set_cookie(
                self.session_cookie,
                encoded,
                max_age=self.max_age,
                httponly=True,
                samesite=self.same_site,
                secure=self.https_only,
                path="/"  # Session cookie needs to be available for all authenticated routes
            )
            logger.debug(f"Successfully set session cookie with data: {session_data}")
        except Exception as e:
            logger.error(f"Failed to set session cookie: {e}")
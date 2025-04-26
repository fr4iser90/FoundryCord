"""
State Snapshot Controller - API for securely capturing and accessing state snapshots
"""
from typing import Dict, Any, List, Optional
from fastapi import Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service
from app.shared.domain.auth.services import AuthenticationService
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.interface.logging.api import get_web_logger
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
import time
import uuid

logger = get_web_logger()

# Models
class StateCollectorInfo(BaseModel):
    """Information about an available state collector"""
    name: str
    description: str
    requires_approval: bool
    scope: str
    is_approved: bool

class SnapshotResult(BaseModel):
    """Result of a state collection operation"""
    timestamp: float
    results: Dict[str, Any]
    
class StateSnapshotRequest(BaseModel):
    """Request to collect state with specific collectors"""
    collectors: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    
class ApprovalRequest(BaseModel):
    """Request to approve a state collector"""
    collector_name: str

class StateSecurityToken(BaseModel):
    """Security token for state collection"""
    token: str
    expires_at: float

# Dependency to get state snapshot service
def get_snapshot_service():
    """Dependency to get the state snapshot service"""
    return get_state_snapshot_service()

# Define the Controller Class
class StateSnapshotController(BaseController):
    """Controller for state snapshot functionality"""
    
    def __init__(self):
        super().__init__(prefix="/owner/state", tags=["State Management"])
        # Get the service instance during initialization
        self.snapshot_service = get_state_snapshot_service()
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Use self.router from BaseController
        self.router.get("/collectors", response_model=List[StateCollectorInfo])(self.get_available_collectors)
        self.router.post("/approve", status_code=status.HTTP_200_OK)(self.approve_collector)
        self.router.post("/snapshot", response_model=SnapshotResult)(self.create_snapshot)
        self.router.get("/token", response_model=StateSecurityToken)(self.get_state_token)

    # --- Route Handler Methods (moved inside class) ---

    async def get_available_collectors(
        self,
        scope: Optional[str] = None,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """Get information about available state collectors"""
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not current_user.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
        collectors = self.snapshot_service.get_available_collectors(scope)
        return collectors

    async def approve_collector(
        self,
        approval: ApprovalRequest,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """Approve a state collector for use"""
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not current_user.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
        approved = self.snapshot_service.approve_collector(
            approval.collector_name, 
            user_id=str(current_user.id)
        )
        
        if not approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to approve collector: {approval.collector_name}"
            )
            
        return {"status": "approved", "collector": approval.collector_name}

    async def create_snapshot(
        self,
        request: Request,
        snapshot_request: StateSnapshotRequest,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """Create a new state snapshot using specified collectors"""
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not current_user.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        # Verify security token if sent from browser
        security_token = request.headers.get("X-State-Security-Token")
        if security_token:
            # TODO: Verify token validity (would use your auth service in production)
            pass
            
        context = {
            **snapshot_request.context,
            "user_id": str(current_user.id),
            "request_ip": request.client.host,
            "user_agent": request.headers.get("User-Agent", ""),
            "timestamp": time.time()
        }
        
        result = await self.snapshot_service.collect_state(
            snapshot_request.collectors,
            context=context
        )
        
        return result

    async def get_state_token(
        self,
        response: Response,
        current_user: AppUserEntity = Depends(get_current_user),
        auth_service: AuthenticationService = Depends(lambda: AuthenticationService(None)) 
    ):
        """Get a security token for state collection"""
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not current_user.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
        token = str(uuid.uuid4())
        expires_at = time.time() + (30 * 60)  # 30 minutes
        
        response.set_cookie(
            key="state_security_token",
            value=token,
            httponly=True,
            max_age=1800, # 30 minutes
            samesite="strict"
        )
        
        return {
            "token": token,
            "expires_at": expires_at
        }

# Instantiate the controller class for export
state_snapshot_controller = StateSnapshotController() 
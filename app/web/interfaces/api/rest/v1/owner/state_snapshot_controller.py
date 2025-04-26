"""
State Snapshot Controller - API for securely capturing and accessing state snapshots
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service
from app.shared.domain.auth.services import AuthenticationService
from app.web.core.extensions.auth import get_current_user
from app.shared.interface.logging.api import get_web_logger
import time
import uuid

logger = get_web_logger()
router = APIRouter(prefix="/owner/state", tags=["state"])

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

# Routes
@router.get("/collectors", response_model=List[StateCollectorInfo])
async def get_available_collectors(
    scope: Optional[str] = None,
    snapshot_service = Depends(get_snapshot_service),
    current_user = Depends(get_current_user)
):
    """Get information about available state collectors"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    collectors = snapshot_service.get_available_collectors(scope)
    return collectors

@router.post("/approve", status_code=status.HTTP_200_OK)
async def approve_collector(
    approval: ApprovalRequest,
    snapshot_service = Depends(get_snapshot_service),
    current_user = Depends(get_current_user)
):
    """Approve a state collector for use"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    approved = snapshot_service.approve_collector(
        approval.collector_name, 
        user_id=str(current_user.id)
    )
    
    if not approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve collector: {approval.collector_name}"
        )
        
    return {"status": "approved", "collector": approval.collector_name}

@router.post("/snapshot", response_model=SnapshotResult)
async def create_snapshot(
    request: Request,
    snapshot_request: StateSnapshotRequest,
    snapshot_service = Depends(get_snapshot_service),
    current_user = Depends(get_current_user)
):
    """Create a new state snapshot using specified collectors"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Verify security token if sent from browser
    security_token = request.headers.get("X-State-Security-Token")
    if security_token:
        # Verify token validity (would use your auth service in production)
        # This is simplified for this implementation
        pass
        
    # Add request context information
    context = {
        **snapshot_request.context,
        "user_id": str(current_user.id),
        "request_ip": request.client.host,
        "user_agent": request.headers.get("User-Agent", ""),
        "timestamp": time.time()
    }
    
    # Collect state using the service
    result = await snapshot_service.collect_state(
        snapshot_request.collectors,
        context=context
    )
    
    return result

@router.get("/token", response_model=StateSecurityToken)
async def get_state_token(
    response: Response,
    current_user = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(lambda: AuthenticationService(None))
):
    """Get a security token for state collection"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    # Generate a temporary token (in production would use your JWT system)
    token = str(uuid.uuid4())
    expires_at = time.time() + (30 * 60)  # 30 minutes
    
    # In a real implementation, store this with the user session
    # Here we're just returning it
    response.set_cookie(
        key="state_security_token",
        value=token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="strict"
    )
    
    return {
        "token": token,
        "expires_at": expires_at
    } 
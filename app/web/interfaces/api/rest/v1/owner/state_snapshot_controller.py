"""
State Snapshot Controller - API for securely capturing and accessing state snapshots
"""
from typing import Dict, Any, List, Optional
from fastapi import Depends, HTTPException, Request, Response, status, Path, APIRouter, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service, SecureStateSnapshot
from app.shared.domain.auth.services import AuthenticationService
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user, get_web_db_session
from app.shared.interface.logging.api import get_web_logger
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.application.services.monitoring.state_snapshot_service import save_snapshot_with_limit, get_snapshot_by_id, list_recent_snapshots
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

class InternalSnapshotTriggerRequest(BaseModel):
    """Request for triggering internal snapshots"""
    collectors: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=lambda: {"trigger": "internal_api"})

class InternalSnapshotTriggerResponse(BaseModel):
    """Response after triggering internal snapshot"""
    status: str
    snapshot_id: str

class StoredSnapshotResponse(BaseModel):
    """Response containing a previously stored snapshot"""
    # Define structure based on what store_snapshot saves
    snapshot_id: str
    capture_timestamp: Optional[float] = None
    trigger_context: Dict[str, Any]
    snapshot: SnapshotResult # Re-use existing model

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
        self.snapshot_service: SecureStateSnapshot = get_state_snapshot_service() # Type hinting
        self._register_routes()
        # Register internal router separately
        self._register_internal_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Use self.router from BaseController
        self.router.get("/collectors", response_model=List[StateCollectorInfo])(self.get_available_collectors)
        self.router.post("/approve", status_code=status.HTTP_200_OK)(self.approve_collector)
        self.router.post("/snapshot", response_model=SnapshotResult)(self.create_snapshot)
        # Endpoint for frontend-triggered snapshots (e.g., JS errors)
        self.router.post("/log-browser-snapshot", status_code=status.HTTP_202_ACCEPTED)(self.log_browser_snapshot)
        self.router.get("/token", response_model=StateSecurityToken)(self.get_state_token)
        # Add route to retrieve stored snapshot
        self.router.get(
            "/snapshot/{snapshot_id}", 
            response_model=StoredSnapshotResponse,
            summary="Retrieve a Stored Snapshot by ID"
        )(self.get_stored_snapshot)
        # Add route to list recent snapshots
        self.router.get(
            "/snapshots/list",
            response_model=List[StoredSnapshotResponse], # Return a list of snapshots
            summary="List Recent Stored Snapshots"
        )(self.list_snapshots)

    def _register_internal_routes(self):
        """Register routes intended for internal system use."""
        # Note: Consider adding internal auth/IP restrictions later
        # These routes are separated to potentially apply different middleware/auth
        internal_router = APIRouter(prefix="/internal/state", tags=["Internal State"])
        internal_router.post(
            "/trigger-snapshot", 
            response_model=InternalSnapshotTriggerResponse,
            summary="Trigger and Store a Server-Side Snapshot"
        )(self.trigger_internal_snapshot)
        # Include this internal router into the main app elsewhere or pass it back
        # For now, assume it gets included. If BaseController manages routers, adjust.
        # Let's attach it to the main router of this controller for simplicity now.
        self.router.include_router(internal_router) 

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
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
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
        
        # --- Save the snapshot to the database --- 
        if result and result.get('results'): # Check if collection was successful
            logger.info(f"Snapshot collected, attempting to save to DB for trigger: user_capture")
            saved_snapshot = await save_snapshot_with_limit(
                db=db,
                trigger='user_capture', # Explicitly set trigger for this endpoint
                snapshot_data=result['results'], # Pass the actual results dict
                context=context # Pass the context we built
                # limit can use the default from the service function
            )
            if saved_snapshot:
                logger.info(f"Snapshot successfully saved to DB with ID: {saved_snapshot.id}")
            else:
                logger.error("Failed to save snapshot to DB after collection.")
                # Decide if we should raise an error here or just log?
                # For now, just log, as the frontend primarily needs the collected data.
        else:
            logger.warning("Snapshot collection did not return valid results, skipping save.")
        # ------------------------------------------

        return result

    async def log_browser_snapshot(
        self,
        request: Request, # To potentially get IP, User-Agent if needed
        snapshot: SnapshotResult = Body(...), # Expect the snapshot data in the body
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """Receives and logs a snapshot captured by the browser (e.g., on JS error)."""
        logger.info("Received request to log browser-captured snapshot.")

        # Basic context, could be enhanced with data from request headers if necessary
        context = snapshot.results.get('context', {}) # Try to get context from snapshot itself
        context['request_ip'] = request.client.host
        context['user_agent'] = request.headers.get("User-Agent", "")
        # Ensure the trigger is set correctly
        trigger = context.get('trigger', 'js_error') # Default to js_error if not provided
        if trigger != 'js_error':
            logger.warning(f"log_browser_snapshot called with unexpected trigger '{trigger}' in context. Forcing to 'js_error'.")
            trigger = 'js_error'

        saved_snapshot = await save_snapshot_with_limit(
            db=db,
            trigger=trigger,
            snapshot_data=snapshot.results, # Pass the results dict
            context=context
        )

        if saved_snapshot:
            logger.info(f"Browser snapshot successfully saved to DB with ID: {saved_snapshot.id}")
            return {"status": "logged", "snapshot_id": str(saved_snapshot.id)}
        else:
            logger.error("Failed to save browser snapshot to DB.")
            # Return 202 Accepted anyway? Or a 500? 
            # Let's return 500 as saving failed.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save snapshot."
            )

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

    async def trigger_internal_snapshot(
        self,
        trigger_request: InternalSnapshotTriggerRequest = Body(...),
        db: AsyncSession = Depends(get_web_db_session),
        # TODO: Add internal auth dependency here if needed
        # internal_auth: bool = Depends(verify_internal_request) 
    ):
        """Triggers server-side state collection and stores the snapshot."""
        logger.info(f"Internal request received to trigger snapshot. Context: {trigger_request.context}")
        
        context = {
            **(trigger_request.context or {}),
            "triggered_at": time.time(),
            # Add any other relevant internal context
        }
        # Determine trigger from context, default to 'internal_api'
        trigger = context.get('trigger', 'internal_api')
        
        try:
            # Use default collectors if none specified?
            # For now, require collectors to be specified or use service default?
            # Let's assume collect_state handles empty list if needed.
            snapshot_result_dict = await self.snapshot_service.collect_state(
                trigger_request.collectors,
                context=context
            )
            
            # Validate if snapshot_result_dict matches SnapshotResult model
            snapshot_result_model = SnapshotResult(**snapshot_result_dict)
            
            # --- Save using the new service --- 
            saved_snapshot = await save_snapshot_with_limit(
                db=db,
                trigger=trigger,
                snapshot_data=snapshot_result_model.results, # Pass the results dict
                context=context
                # Use default limit
            )
            
            if saved_snapshot:
                logger.info(f"Internal snapshot triggered and saved successfully. ID: {saved_snapshot.id}")
                return {"status": "success", "snapshot_id": str(saved_snapshot.id)}
            else:
                logger.error("Failed to save internal snapshot to DB after collection.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save snapshot after collection."
                )
            # ---------------------------------
        
        except Exception as e:
            logger.error(f"Failed to trigger or store internal snapshot: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to trigger or store snapshot"
            )
            
    async def get_stored_snapshot(
        self,
        snapshot_id: str = Path(..., title="Snapshot ID", description="The unique ID of the snapshot to retrieve"),
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """Retrieve a previously stored state snapshot by its ID."""
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not current_user.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        logger.info(f"User {current_user.username} requesting stored snapshot ID: {snapshot_id}")
        
        snapshot = await get_snapshot_by_id(db, snapshot_id)
        
        if snapshot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Snapshot with ID '{snapshot_id}' not found."
            )
            
        # Validate/parse the stored data into the response model
        try:
            # Construct the response based on the retrieved snapshot object
            # Assuming SnapshotResult can be created from snapshot.snapshot_data
            snapshot_result_data = SnapshotResult(
                timestamp=snapshot.timestamp.timestamp(), # Convert datetime to float timestamp
                results=snapshot.snapshot_data
            )
            response_data = StoredSnapshotResponse(
                snapshot_id=str(snapshot.id),
                capture_timestamp=snapshot.timestamp.timestamp(), # Use float timestamp
                trigger_context=snapshot.context or {},
                snapshot=snapshot_result_data
            )
            return response_data
        except Exception as e:
             logger.error(f"Failed to parse stored snapshot data for ID {snapshot_id}: {e}", exc_info=True)
             raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail="Failed to parse stored snapshot data."
             )

    async def list_snapshots(
        self,
        limit: int = 10, # Allow specifying limit via query parameter, default to 10
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """Lists the most recent stored snapshots."""
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not current_user.is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        logger.info(f"User {current_user.username} requesting list of recent snapshots (limit: {limit})")
        
        # Use the service function
        snapshots = await list_recent_snapshots(db, count=limit)

        # Convert the list of StateSnapshot objects to a list of StoredSnapshotResponse objects
        response_list = []
        for snapshot in snapshots:
            try:
                snapshot_result_data = SnapshotResult(
                    timestamp=snapshot.timestamp.timestamp(),
                    results=snapshot.snapshot_data
                )
                response_data = StoredSnapshotResponse(
                    snapshot_id=str(snapshot.id),
                    capture_timestamp=snapshot.timestamp.timestamp(),
                    trigger_context=snapshot.context or {},
                    snapshot=snapshot_result_data
                )
                response_list.append(response_data)
            except Exception as e:
                logger.error(f"Failed to parse snapshot data for list (ID: {snapshot.id}): {e}", exc_info=True)
                # Optionally skip this snapshot or add a placeholder?
                # Let's skip it for now to avoid sending malformed data.
                continue 

        return response_list

# Instantiate the controller class for export
state_snapshot_controller = StateSnapshotController() 
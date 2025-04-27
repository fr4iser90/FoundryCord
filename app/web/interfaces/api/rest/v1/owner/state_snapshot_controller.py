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
from app.shared.application.services.monitoring.state_snapshot_service import save_snapshot_with_limit, get_snapshot_by_id, list_recent_snapshots, delete_snapshot_by_id
from app.web.interfaces.api.rest.v1.schemas.state_monitor_schemas import (
    StateSnapshotMetadata, StoredSnapshotResponse, BrowserSnapshotResults, FullSnapshotData # Import needed schemas
)
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

# Dependency to get state snapshot service
def get_snapshot_service():
    """Dependency to get the state snapshot service"""
    return get_state_snapshot_service()

# Dependency for owner check (assuming it uses get_current_user like others)
def verify_owner(current_user: AppUserEntity = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if not current_user.is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return current_user

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
        # NOW REQUIRES OWNER AUTH
        self.router.post(
            "/log-browser-snapshot", 
            status_code=status.HTTP_202_ACCEPTED,
            dependencies=[Depends(verify_owner)] # ADD OWNER AUTH DEPENDENCY
        )(self.log_browser_snapshot)
        
        self.router.get("/token", response_model=StateSecurityToken)(self.get_state_token)
        
        # --- Snapshot Routes (Order Matters!) ---
        
        # List route FIRST (more specific)
        self.router.get(
            "/snapshots/list",
            # response_model=List[StoredSnapshotResponse], <-- Use StateSnapshotMetadata for list
            response_model=List[StateSnapshotMetadata],
            summary="List Recent Stored Snapshots",
            dependencies=[Depends(verify_owner)] # Secure list endpoint
        )(self.list_snapshots)
        
        # Retrieve single route SECOND (less specific)
        self.router.get(
            "/snapshots/{snapshot_id}", 
            response_model=StoredSnapshotResponse,
            summary="Retrieve a Stored Snapshot by ID",
            dependencies=[Depends(verify_owner)] # Secure retrieve endpoint
        )(self.get_stored_snapshot)
        
        # Delete route (also uses ID)
        self.router.delete(
            "/snapshots/{snapshot_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a Stored Snapshot by ID",
            dependencies=[Depends(verify_owner)] # Secure delete endpoint
        )(self.delete_snapshot)
        # --- End Snapshot Routes ---

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
                # Add snapshot_id to the result returned to frontend? Optional.
                result['snapshot_id'] = str(saved_snapshot.id)
            else:
                logger.error("Failed to save snapshot to DB after collection.")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Snapshot collected but failed to save to database. Check server logs."
                )
        else:
            logger.warning("Snapshot collection did not return valid results, skipping save.")
            # Raise an error here too? If results are expected but missing.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Snapshot collection failed or returned no results."
            )
        # ------------------------------------------

        # Only return result if saving was successful (or if saving is not critical)
        return result

    async def log_browser_snapshot(
        self,
        request: Request, # Keep for IP/User-Agent if still desired
        # REMOVE specific SnapshotLogPayload validation
        # payload: SnapshotLogPayload, 
        # Use a more generic dict or simple BaseModel if basic check is needed
        payload: Dict[str, Any] = Body(...), # Accept generic dictionary
        db: AsyncSession = Depends(get_web_db_session),
        # REMOVE Header check 
        # x_snapshot_source: Optional[str] = Header(None),
        # Auth is now handled by Depends(verify_owner) in the route decorator
        current_owner: AppUserEntity = Depends(verify_owner) # Inject verified owner 
    ):
        """Receives and logs a snapshot captured by the browser (e.g., on JS error). REQUIRES OWNER AUTH."""
        logger.info(f"Owner {current_owner.id} logging browser-captured snapshot.")
        
        # REMOVE Header validation
        # if x_snapshot_source != "JS-Error-Handler": 
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing or invalid snapshot source header")

        # Basic context extraction (less critical now with auth)
        # Extract results and context carefully from the generic payload dict
        results_data = payload.get('results')
        context_data = payload.get('context', {}) # Default to empty dict
        trigger = context_data.get('trigger', 'js_error') # Still useful to record trigger
        
        if not results_data:
            logger.warning("Received browser snapshot log request with missing 'results' data.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing snapshot results data")
        
        # Add owner ID to context if not present?
        context_data['owner_id'] = str(current_owner.id) 
        context_data['request_ip'] = request.client.host
        context_data['user_agent'] = request.headers.get("User-Agent", "")

        # Ensure trigger is js_error if coming through this route
        if trigger != 'js_error':
             logger.warning(f"log_browser_snapshot called by owner {current_owner.id} with unexpected trigger '{trigger}'. Forcing to 'js_error'.")
             trigger = 'js_error'
             context_data['trigger'] = trigger # Update context

        saved_snapshot = await save_snapshot_with_limit(
            db=db,
            trigger=trigger,
            snapshot_data=results_data, # Pass the extracted results dict
            context=context_data # Pass the potentially modified context dict
        )

        if not saved_snapshot:
            # Consider different error if save fails
            logger.error(f"Failed to save browser snapshot logged by owner {current_owner.id}.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save snapshot")

        logger.info(f"Browser snapshot logged by owner {current_owner.id} saved with ID: {saved_snapshot.id}")
        # Return 202 Accepted - we took the data, processing happened
        return Response(status_code=status.HTTP_202_ACCEPTED)

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
            # Extract server and browser data from the stored snapshot_data dict
            snapshot_dict = snapshot.snapshot_data or {}
            server_data = snapshot_dict.get('server')
            browser_data_dict = snapshot_dict.get('browser')
            
            # Parse browser data using the existing schema if available
            browser_results = None
            if browser_data_dict:
                try:
                    browser_results = BrowserSnapshotResults(**browser_data_dict)
                except Exception as parse_err:
                    logger.warning(f"Failed to parse browser results for snapshot {snapshot_id}: {parse_err}")
                    # Decide how to handle - maybe keep the raw dict?
                    # For now, let's proceed without parsed browser data if it fails

            # Construct the nested FullSnapshotData object
            full_snapshot_data_obj = FullSnapshotData(
                server=server_data,
                browser=browser_results # Assign the parsed BrowserSnapshotResults object
            )

            # Construct the final StoredSnapshotResponse object correctly
            response_data = StoredSnapshotResponse(
                snapshot_id=str(snapshot.id),
                capture_timestamp=snapshot.timestamp.timestamp(), # Use float timestamp
                trigger=snapshot.trigger, # Add the missing trigger field
                context=snapshot.context or {}, # Use context from DB
                snapshot=full_snapshot_data_obj # Assign the correctly typed object
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
        limit: int = 10,
        # current_user: AppUserEntity = Depends(get_current_user), # Already checked by route dependency
        db: AsyncSession = Depends(get_web_db_session),
        # Ensure verify_owner dependency is implicitly handled by the route decorator
    ):
        """Lists the most recent stored snapshots (metadata only)."""
        # logger.info(f"User {current_user.username} requesting list of recent snapshots (limit: {limit})")
        
        # Use the service function to get full snapshot objects
        snapshots = await list_recent_snapshots(db, count=limit)

        # Convert the list of StateSnapshot objects to a list of StateSnapshotMetadata objects
        metadata_list = []
        for snapshot in snapshots:
            try:
                metadata = StateSnapshotMetadata(
                    snapshot_id=str(snapshot.id),
                    capture_timestamp=snapshot.timestamp.timestamp(), # Use float timestamp
                    trigger=snapshot.trigger,
                    context=snapshot.context or {} # Ensure context is at least an empty dict
                )
                metadata_list.append(metadata)
            except Exception as e:
                logger.error(f"Failed to parse snapshot metadata for list (ID: {snapshot.id}): {e}", exc_info=True)
                # Skip this snapshot if parsing fails
                continue 
        
        # logger.debug(f"Returning metadata for {len(metadata_list)} snapshots.")
        return metadata_list

    async def delete_snapshot(
        self,
        snapshot_id: str = Path(..., title="Snapshot ID", description="The unique ID of the snapshot to delete"),
        # current_user: AppUserEntity = Depends(get_current_user), # Checked by route dependency
        db: AsyncSession = Depends(get_web_db_session),
        current_owner: AppUserEntity = Depends(verify_owner) # Inject owner for logging context
    ):
        """Deletes a stored state snapshot by its ID."""
        # logger.info(f"User {current_owner.username} requesting deletion of snapshot ID: {snapshot_id}")

        deleted = await delete_snapshot_by_id(db, snapshot_id)

        if not deleted:
            # Check if it existed first?
            snapshot = await get_snapshot_by_id(db, snapshot_id)
            if snapshot is None:
                # Raise 404 if it never existed
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Snapshot with ID '{snapshot_id}' not found."
                )
            else:
                # It existed but deletion failed
                logger.error(f"Failed to delete snapshot {snapshot_id} from database.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete snapshot {snapshot_id}. Check server logs."
                )
                
        # logger.info(f"Successfully deleted snapshot ID: {snapshot_id}")
        # Return 204 No Content on success, which FastAPI handles by returning None
        return None

# Instantiate the controller class for export
state_snapshot_controller = StateSnapshotController() 
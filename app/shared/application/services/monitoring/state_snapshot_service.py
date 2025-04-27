from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging
from typing import Dict, Any, Optional, List

# Assuming the model is defined here relative to the shared infrastructure
from app.shared.infrastructure.models.monitoring.state_snapshot import StateSnapshot

logger = logging.getLogger(__name__)

DEFAULT_SNAPSHOT_LIMIT = 10

def save_snapshot_with_limit(
    db: Session, 
    trigger: str, 
    snapshot_data: Dict[str, Any], 
    context: Optional[Dict[str, Any]] = None, 
    limit: int = DEFAULT_SNAPSHOT_LIMIT
) -> Optional[StateSnapshot]:
    """
    Saves a new state snapshot to the database and enforces a limit 
    on the total number of stored snapshots by deleting the oldest ones.

    Args:
        db: The SQLAlchemy database session.
        trigger: The reason the snapshot was triggered (e.g., 'user_capture').
        snapshot_data: The main JSON data of the snapshot.
        context: Optional context metadata for the snapshot.
        limit: The maximum number of snapshots to keep.

    Returns:
        The saved StateSnapshot object if successful, None otherwise.
    """
    logger.info(f"Attempting to save state snapshot triggered by: {trigger}")
    try:
        # 1. Create the new snapshot object
        new_snapshot = StateSnapshot(
            trigger=trigger,
            snapshot_data=snapshot_data,
            context=context
            # timestamp is handled by server_default
        )
        db.add(new_snapshot)
        logger.debug(f"New snapshot created (ID pending commit): {new_snapshot.id}")

        # 2. Enforce the limit (delete oldest if necessary)
        # It's often safer to commit the new one first, then delete, 
        # but deleting first can prevent exceeding the limit even temporarily.
        # Let's delete first for stricter limit enforcement.

        # Count existing snapshots
        current_count = db.query(StateSnapshot).count()
        logger.debug(f"Current snapshot count: {current_count}, Limit: {limit}")

        if current_count >= limit:
            # Calculate how many to delete
            num_to_delete = (current_count - limit) + 1 # +1 because we are adding a new one
            logger.info(f"Snapshot limit ({limit}) reached/exceeded. Deleting {num_to_delete} oldest snapshot(s).")
            
            # Find the oldest snapshots
            oldest_snapshots = db.query(StateSnapshot).order_by(StateSnapshot.timestamp.asc()).limit(num_to_delete).all()
            
            for snapshot_to_delete in oldest_snapshots:
                logger.debug(f"Deleting old snapshot: ID={snapshot_to_delete.id}, Timestamp={snapshot_to_delete.timestamp}")
                db.delete(snapshot_to_delete)

        # 3. Commit the transaction (adds new snapshot, deletes old ones)
        db.commit()
        db.refresh(new_snapshot) # Refresh to get the generated ID and timestamp
        logger.info(f"Successfully saved snapshot ID: {new_snapshot.id}")
        return new_snapshot

    except Exception as e:
        logger.error(f"Error saving state snapshot: {e}", exc_info=True)
        db.rollback() # Roll back the transaction on error
        return None

# --- Placeholder functions for retrieval (to be implemented based on TODO) --- 

def get_snapshot_by_id(db: Session, snapshot_id: str) -> Optional[StateSnapshot]:
    """Retrieves a single snapshot by its UUID."""
    logger.debug(f"Fetching snapshot by ID: {snapshot_id}")
    try:
        # Attempt to convert string ID to UUID for querying
        import uuid
        snapshot_uuid = uuid.UUID(snapshot_id)
        snapshot = db.query(StateSnapshot).filter(StateSnapshot.id == snapshot_uuid).first()
        if snapshot:
            logger.info(f"Snapshot found for ID: {snapshot_id}")
        else:
            logger.warning(f"Snapshot not found for ID: {snapshot_id}")
        return snapshot
    except ValueError:
        logger.error(f"Invalid UUID format provided for snapshot ID: {snapshot_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching snapshot by ID {snapshot_id}: {e}", exc_info=True)
        return None

def list_recent_snapshots(db: Session, count: int = DEFAULT_SNAPSHOT_LIMIT) -> List[StateSnapshot]: # Use constant
    """Retrieves the most recent snapshots, up to the specified count."""
    logger.debug(f"Fetching {count} recent snapshots")
    try:
        snapshots = db.query(StateSnapshot).order_by(StateSnapshot.timestamp.desc()).limit(count).all()
        logger.info(f"Retrieved {len(snapshots)} recent snapshots.")
        return snapshots
    except Exception as e:
        logger.error(f"Error fetching recent snapshots: {e}", exc_info=True)
        return [] # Return empty list on error 
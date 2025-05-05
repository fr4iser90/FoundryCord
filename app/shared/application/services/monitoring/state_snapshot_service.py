from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, delete, func
import logging
from typing import Dict, Any, Optional, List

# Assuming the model is defined here relative to the shared infrastructure
from app.shared.infrastructure.models.monitoring.state_snapshot import StateSnapshot
from app.shared.interfaces.logging.api import get_shared_logger
import uuid
from datetime import datetime, timezone

logger = get_shared_logger()

DEFAULT_SNAPSHOT_LIMIT = 20

async def save_snapshot_with_limit(
    db: AsyncSession, 
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
    logger.info(f"Attempting to save snapshot triggered by '{trigger}'. Limit: {limit}. Context keys: {list(context.keys()) if context else 'None'}")
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

        # 2. Commit the new snapshot first to ensure it's in the DB before potentially deleting old ones
        await db.commit()
        await db.refresh(new_snapshot) # Refresh to get the full object with relationships if any
        logger.info(f"Successfully added new snapshot {new_snapshot.id} for trigger '{trigger}'.")

        # 3. Enforce the limit asynchronously
        # Count existing snapshots AFTER adding the new one
        count_query = select(func.count(StateSnapshot.id)).where(StateSnapshot.trigger == trigger)
        count_result = await db.execute(count_query)
        existing_count_after_add = count_result.scalar_one()
        logger.debug(f"Total snapshots for trigger '{trigger}' after adding: {existing_count_after_add}")

        if existing_count_after_add > limit:
            num_to_delete = existing_count_after_add - limit
            logger.info(f"Limit ({limit}) exceeded. Deleting {num_to_delete} oldest snapshot(s) for trigger '{trigger}'.")

            # Find the IDs of the oldest snapshots to delete
            select_oldest_query = select(StateSnapshot.id) \
                                  .where(StateSnapshot.trigger == trigger) \
                                  .order_by(StateSnapshot.timestamp.asc()) \
                                  .limit(num_to_delete)
            
            result_oldest = await db.execute(select_oldest_query)
            ids_to_delete = [row.id for row in result_oldest]

            if ids_to_delete:
                delete_query = delete(StateSnapshot).where(StateSnapshot.id.in_(ids_to_delete))
                await db.execute(delete_query)
                logger.info(f"Successfully deleted {len(ids_to_delete)} old snapshots for trigger '{trigger}'.")

        await db.commit()
        return new_snapshot

    except Exception as e:
        logger.error(f"Error saving state snapshot: {e}", exc_info=True)
        await db.rollback() # Roll back the transaction on error
        return None

# --- Placeholder functions for retrieval (to be implemented based on TODO) --- 

async def get_snapshot_by_id(db: AsyncSession, snapshot_id: str) -> Optional[StateSnapshot]:
    """
    Retrieves a single state snapshot by its unique ID asynchronously.

    :param db: The SQLAlchemy database session.
    :param snapshot_id: The UUID string of the snapshot to retrieve.
    :return: The StateSnapshot object if found, otherwise None.
    """
    logger.debug(f"Attempting to retrieve snapshot with ID: {snapshot_id}")
    try:
        # Validate if snapshot_id is a valid UUID format
        parsed_id = uuid.UUID(snapshot_id)
        # Use select with get for primary key lookup (more efficient)
        # snapshot = await db.get(StateSnapshot, parsed_id) # .get might not work directly with UUIDs depending on dialect config? Fallback to select.
        query = select(StateSnapshot).where(StateSnapshot.id == parsed_id)
        result = await db.execute(query)
        snapshot = result.scalar_one_or_none() # Use scalar_one_or_none for single result or None
        
        if snapshot:
            logger.debug(f"Snapshot found: {snapshot.id}")
        else:
            logger.warning(f"Snapshot with ID '{snapshot_id}' not found.")
        return snapshot
    except ValueError: # Catch invalid UUID format
        logger.error(f"Invalid UUID format provided for snapshot_id: '{snapshot_id}'")
        return None
    except Exception as e:
        logger.error(f"Error retrieving snapshot by ID {snapshot_id}: {e}", exc_info=True)
        return None

async def list_recent_snapshots(db: AsyncSession, count: int = 10) -> List[StateSnapshot]:
    """
    Lists the most recent state snapshots, ordered by timestamp descending.

    :param db: The SQLAlchemy database session.
    :param count: The maximum number of snapshots to return.
    :return: A list of StateSnapshot objects.
    """
    logger.debug(f"Listing the latest {count} snapshots.")
    try:
        query = select(StateSnapshot) \
                .order_by(StateSnapshot.timestamp.desc()) \
                .limit(count)
        result = await db.execute(query)
        snapshots = result.scalars().all() # Get all results as model instances
        logger.debug(f"Found {len(snapshots)} recent snapshots (limit was {count}).")
        return snapshots
    except Exception as e:
        logger.error(f"Error listing recent snapshots: {e}", exc_info=True)
        return [] # Return empty list on error
        
async def delete_snapshot_by_id(db: AsyncSession, snapshot_id: str) -> bool:
    """
    Deletes a state snapshot by its unique ID asynchronously.

    :param db: The SQLAlchemy database session.
    :param snapshot_id: The UUID string of the snapshot to delete.
    :return: True if the snapshot was found and deleted, False otherwise.
    """
    logger.info(f"Attempting to delete snapshot with ID: {snapshot_id}")
    try:
        # Validate if snapshot_id is a valid UUID format first
        parsed_id = uuid.UUID(snapshot_id)
    except ValueError:
        logger.error(f"Invalid UUID format provided for deletion: '{snapshot_id}'")
        return False

    try:
        # Use the existing get_snapshot_by_id to check if it exists first
        # Although not strictly necessary with delete, it helps confirm existence before attempting delete
        snapshot_to_delete = await get_snapshot_by_id(db, snapshot_id) # Use the already validated parsed_id? No, get_snapshot_by_id handles string

        if snapshot_to_delete is None:
            logger.warning(f"Snapshot with ID '{snapshot_id}' not found for deletion.")
            return False # Return False if not found

        # If found, proceed with deletion
        logger.debug(f"Snapshot {snapshot_id} found. Proceeding with deletion.")
        # Option 1: Delete the object directly
        await db.delete(snapshot_to_delete)
        # Option 2: Use a delete query (might be slightly more efficient if object not needed)
        # delete_stmt = delete(StateSnapshot).where(StateSnapshot.id == parsed_id)
        # result = await db.execute(delete_stmt)
        # if result.rowcount == 0: # Check if any row was actually deleted
        #     logger.warning(f"Snapshot with ID '{snapshot_id}' was found but delete query affected 0 rows.")
        #     await db.rollback() # Rollback if delete seemed to fail
        #     return False

        await db.commit() # Commit the deletion
        logger.info(f"Successfully deleted snapshot with ID: {snapshot_id}")
        return True

    except Exception as e:
        logger.error(f"Error deleting snapshot {snapshot_id}: {e}", exc_info=True)
        await db.rollback() # Roll back the transaction on any error during delete/commit
        return False 
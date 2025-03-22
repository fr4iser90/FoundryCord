import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

class DatabaseHandler(logging.Handler):
    """
    Logging handler that stores log records in database.
    Uses a queue to avoid blocking the application while writing to DB.
    """
    def __init__(self, max_queue_size=1000):
        super().__init__()
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.task = None
        self._start_worker()
    
    def _start_worker(self):
        """Start the async worker to process logs in background"""
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self._process_queue())
    
    async def _process_queue(self):
        """Process log records from the queue"""
        while True:
            try:
                record = await self.queue.get()
                await self._write_to_db(record)
                self.queue.task_done()
            except Exception as e:
                print(f"Error processing log record: {e}")
                await asyncio.sleep(1)  # Avoid tight loop on error
    
    async def _write_to_db(self, log_data: Dict[str, Any]):
        """Write log record to database"""
        try:
            # Lazy import to avoid circular dependencies
            from app.shared.infrastructure.database import get_async_session
            from app.shared.infrastructure.models.log_models import LogEntry
            from sqlalchemy.ext.asyncio import AsyncSession
            
            async with get_async_session() as session:
                session: AsyncSession
                log_entry = LogEntry(
                    timestamp=log_data["created"],
                    level=log_data["levelname"],
                    logger_name=log_data["name"],
                    message=log_data["message"],
                    module=log_data.get("module", ""),
                    function=log_data.get("funcName", ""),
                    line_num=log_data.get("lineno", 0),
                    exception=log_data.get("exc_info", "")
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            print(f"Failed to write log to database: {e}")
    
    def emit(self, record):
        """Add log record to queue for processing"""
        try:
            # Convert record to dict for easier serialization
            log_data = {
                "created": datetime.fromtimestamp(record.created),
                "name": record.name,
                "levelname": record.levelname,
                "levelno": record.levelno,
                "message": self.format(record),
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
                "exc_info": record.exc_info
            }
            
            # Try to add to queue, drop if queue is full
            try:
                if not self.queue.full():
                    asyncio.create_task(self.queue.put(log_data))
            except Exception:
                pass
                
        except Exception as e:
            print(f"Error in DB logging handler: {e}")
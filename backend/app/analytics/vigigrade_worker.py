"""
Background Worker for VigiGrade Score Updates

This module provides background task functionality for automated
confidence score calculations and updates.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.services.scoring import update_case_score, batch_update_scores

logger = logging.getLogger(__name__)


class VigiGradeWorker:
    """
    Background worker for automated confidence score updates.
    
    Features:
    - Periodic batch updates for all cases
    - Real-time updates for new/modified cases
    - Configurable update intervals
    - Error handling and retry logic
    """
    
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        batch_interval_minutes: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize the VigiGrade background worker.
        
        Args:
            db: MongoDB database instance
            batch_interval_minutes: Minutes between batch updates (default: 60)
            max_retries: Maximum retry attempts for failed updates (default: 3)
        """
        self.db = db
        self.batch_interval = timedelta(minutes=batch_interval_minutes)
        self.max_retries = max_retries
        self.is_running = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def update_single_case(
        self,
        case_id: str,
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Update confidence score for a single case with retry logic.
        
        Args:
            case_id: Case identifier
            retry_count: Current retry attempt number
            
        Returns:
            Score result or None if all retries fail
        """
        try:
            result = await update_case_score(case_id, self.db)
            
            if result:
                self.logger.info(
                    f"Successfully updated case {case_id}: "
                    f"score={result['score']}, grade={result['grade']}"
                )
            
            return result
            
        except Exception as e:
            if retry_count < self.max_retries:
                self.logger.warning(
                    f"Failed to update case {case_id} (attempt {retry_count + 1}): {str(e)}. "
                    f"Retrying..."
                )
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.update_single_case(case_id, retry_count + 1)
            else:
                self.logger.error(
                    f"Failed to update case {case_id} after {self.max_retries} attempts: {str(e)}"
                )
                return None
    
    async def run_batch_update(self) -> Dict[str, Any]:
        """
        Run a full batch update for all cases.
        
        Returns:
            Summary statistics
        """
        self.logger.info("Starting batch score update")
        start_time = datetime.utcnow()
        
        try:
            summary = await batch_update_scores(self.db)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info(
                f"Batch update completed in {duration:.2f}s: "
                f"{summary['successful']} successful, {summary['failed']} failed"
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Batch update failed: {str(e)}", exc_info=True)
            raise
    
    async def periodic_batch_update_loop(self):
        """
        Run periodic batch updates in a loop.
        
        This coroutine runs continuously and performs batch updates
        at the configured interval.
        """
        self.logger.info(
            f"Starting periodic batch update loop "
            f"(interval: {self.batch_interval.total_seconds() / 60:.0f} minutes)"
        )
        
        while self.is_running:
            try:
                await self.run_batch_update()
                
                # Wait for next interval
                await asyncio.sleep(self.batch_interval.total_seconds())
                
            except asyncio.CancelledError:
                self.logger.info("Periodic update loop cancelled")
                break
            except Exception as e:
                self.logger.error(
                    f"Error in periodic update loop: {str(e)}",
                    exc_info=True
                )
                # Wait before retrying
                await asyncio.sleep(60)
    
    async def watch_for_changes(self):
        """
        Watch for new or modified cases and update their scores in real-time.
        
        This uses MongoDB Change Streams to detect changes and trigger
        immediate score updates.
        """
        self.logger.info("Starting change stream watcher")
        
        try:
            # Create change stream for insert and update operations
            pipeline = [
                {
                    "$match": {
                        "operationType": {"$in": ["insert", "update", "replace"]}
                    }
                }
            ]
            
            async with self.db.cases.watch(pipeline) as change_stream:
                async for change in change_stream:
                    if not self.is_running:
                        break
                    
                    try:
                        # Extract case_id from the change event
                        case_id = None
                        
                        if change["operationType"] == "insert":
                            case_id = change["fullDocument"].get("case_id")
                        elif change["operationType"] in ["update", "replace"]:
                            # Fetch the document to get case_id
                            doc = await self.db.cases.find_one(
                                {"_id": change["documentKey"]["_id"]}
                            )
                            if doc:
                                case_id = doc.get("case_id")
                        
                        if case_id:
                            self.logger.info(
                                f"Detected change for case {case_id}, updating score"
                            )
                            await self.update_single_case(case_id)
                        
                    except Exception as e:
                        self.logger.error(
                            f"Error processing change event: {str(e)}",
                            exc_info=True
                        )
                        
        except asyncio.CancelledError:
            self.logger.info("Change stream watcher cancelled")
        except Exception as e:
            self.logger.error(
                f"Change stream error: {str(e)}",
                exc_info=True
            )
    
    async def start(self, enable_change_stream: bool = True):
        """
        Start the background worker.
        
        Args:
            enable_change_stream: Whether to enable real-time change detection
        """
        if self.is_running:
            self.logger.warning("Worker is already running")
            return
        
        self.is_running = True
        self.logger.info("Starting VigiGrade background worker")
        
        tasks = []
        
        # Start periodic batch updates
        batch_task = asyncio.create_task(self.periodic_batch_update_loop())
        tasks.append(batch_task)
        
        # Start change stream watcher if enabled
        if enable_change_stream:
            change_task = asyncio.create_task(self.watch_for_changes())
            tasks.append(change_task)
        
        try:
            # Wait for all tasks
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.info("Worker tasks cancelled")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Stop the background worker gracefully"""
        self.logger.info("Stopping VigiGrade background worker")
        self.is_running = False


async def initialize_worker(
    mongodb_uri: str,
    database_name: str,
    batch_interval_minutes: int = 60
) -> VigiGradeWorker:
    """
    Initialize and return a configured VigiGrade worker.
    
    Args:
        mongodb_uri: MongoDB connection string
        database_name: Name of the database
        batch_interval_minutes: Minutes between batch updates
        
    Returns:
        Configured VigiGradeWorker instance
        
    Example:
        >>> worker = await initialize_worker(
        ...     "mongodb://localhost:27017",
        ...     "pharmacovigilance",
        ...     batch_interval_minutes=30
        ... )
        >>> await worker.start()
    """
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[database_name]
    
    worker = VigiGradeWorker(
        db=db,
        batch_interval_minutes=batch_interval_minutes
    )
    
    return worker


# Standalone script entry point
if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    async def main():
        """Main entry point for standalone worker"""
        # Configuration
        MONGODB_URI = "mongodb://localhost:27017"
        DATABASE_NAME = "pharmacovigilance"
        BATCH_INTERVAL = 60  # minutes
        
        try:
            # Initialize worker
            worker = await initialize_worker(
                mongodb_uri=MONGODB_URI,
                database_name=DATABASE_NAME,
                batch_interval_minutes=BATCH_INTERVAL
            )
            
            logger.info("Worker initialized, starting...")
            
            # Start worker
            await worker.start(enable_change_stream=True)
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Worker failed: {str(e)}", exc_info=True)
            sys.exit(1)
    
    # Run
    asyncio.run(main())

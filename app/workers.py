import time
from sqlalchemy.orm import Session
from .db import SessionLocal
from .crud import update_operation_status, recover_stuck_operations
from .logger import logger
from .metrics import operations_duration_seconds

with operations_duration_seconds.time():
    def execute_operation(operation_id):
        db: Session = SessionLocal()
        try:
            logger.info(
                "Operation_execution_started",
                extra={
                    "operation_id": str(operation_id)
                }
            )
            time.sleep(1)
            update_operation_status(
                db,
                operation_id,
                "SUCCESS"
            )
            logger.info(
                "Operation_execution_succeeded",
                extra={
                    "operation_id": str(operation_id)
                }
            )
        except Exception:
            update_operation_status(
                db,
                operation_id,
                "FAILED"
            )
            logger.error(
                "Operation_execution_failed",
                extra={
                    "operation_id": str(operation_id)
                }
            )
        finally:
            db.close()

def recovery_worker():
    db = SessionLocal()
    try:
        recover_stuck_operations(db)
    finally:
        db.close()
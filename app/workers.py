import time
from sqlalchemy.orm import Session
from .db import SessionLocal
from .crud import update_operation_status, recover_stuck_operations

def execute_operation(operation_id):
    db: Session = SessionLocal()
    try:
        time.sleep(40)
        return
        update_operation_status(
            db,
            operation_id,
            "SUCCESS"
        )
    except Exception:
        update_operation_status(
            db,
            operation_id,
            "FAILED"
        )
    finally:
        db.close()

def recovery_worker():
    db = SessionLocal()
    try:
        recover_stuck_operations(db)
    finally:
        db.close()
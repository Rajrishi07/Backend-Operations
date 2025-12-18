import time
from sqlalchemy.orm import Session
from .db import SessionLocal
from .crud import update_operation_status

def execute_operation(operation_id):
    db: Session = SessionLocal()
    try:
        time.sleep(5)

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
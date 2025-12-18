from sqlalchemy.orm import Session
from .models import Operation
from datetime import datetime

def create_operation(db: Session, operation_type: str) -> Operation:
    op = Operation(
        type=operation_type,
        status="PENDING"
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op

def get_operation(db: Session, operation_id: UUID) -> Operation | None:
    return db.query(Operation).filter(Operation.id == operation_id).first()

ALLOWED_TRANSITIONS = {
    "PENDING" : {"RUNNING"},
    "RUNNING" : {"SUCCESS", "FAILED"},
    "SUCCESS" : set(),
    "FAILED" : set()
}

def update_operation_status(
    db: session,
    operation_id: UUID,
    new_status: str
) -> Operation:

    op = (db.query(Operation)
    .filter(Operation.id == operation_id)
    .with_for_update()
    .first()
    )

    if not op:
        raise ValueError("NOT_FOUND")

    if new_status not in ALLOWED_TRANSITIONS[op.status]:
        raise ValueError(
            f"Invalid Transition {op.status} -> {new_status}"
        )

    op.status = new_status
    op.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(op)
    return op
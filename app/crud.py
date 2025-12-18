from sqlalchemy.orm import Session
from .models import Operation, IdempotencyKey
from datetime import datetime
import hashlib
import json

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

def hash_request(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()

def get_idempotent_response(
    db: Session,
    key: str,
    operation_id: str,
    request_hash: str
):
    record = db.query(IdempotencyKey).filter(
        IdempotencyKey.key == key
    ).first()

    if not record:
        return None
    
    if record.operation_id != operation_id or record.request_hash != request_hash:
        raise ValueError("IDEMPOTENCY_KEY_REUSE")
    return record.response

def save_idempotent_response(
    db: Session,
    key: str,
    operation_id: str,
    request_hash: str,
    response: dict
):
    record = IdempotencyKey(
        key=key,
        operation_id=operation_id,
        request_hash=request_hash,
        response=response
    )
    db.add(record)
    db.commit()

def cache_operation(redis_client, operation_id: str, data: dict, ttl: int = 30):
    redis_client.setex(
        f"operation:{operation_id}",
        ttl,
        json.dumps(data)
    )

def get_cached_operation(redis_client, operation_id: str):
    value = redis_client.get(f"operation:{operation_id}")
    if not value:
        return None
    return json.loads(value)
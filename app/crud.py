from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from .models import Operation, IdempotencyKey
from .logger import logger
from .metrics import operations_created_total
from .metrics import (
    operations_running,
    operations_succeeded_total,
    operations_failed_total,
)
from datetime import datetime, timedelta
import hashlib
import json

def create_operation(db: Session, operation_type: str) -> Operation:
    op = Operation(
        type=operation_type,
        status="PENDING"
    )
    db.add(op)
    db.commit()
    print("Created Operation, Increasing Total")
    operations_created_total.inc()
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
    if op.status == "RUNNING" and new_status in {"SUCCESS", "FAILED"}:
        operations_running.dec()

    if new_status == "RUNNING":
        op.started_at = datetime.utcnow()
        operations_running.inc()
    
    if new_status == "SUCCESS":
        operations_succeeded_total.inc()

    if new_status == "FAILED":
        operations_failed_total.inc()

    
    old_status = op.status
    op.status = new_status
    op.updated_at = datetime.utcnow()

    logger.info(
        "Operation_status_changed",
        extra={
            "operation_id": str(operation_id),
            "from": old_status,
            "to": new_status
        }
    )

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
    safe_data = jsonable_encoder(data)
    redis_client.setex(
        f"operation:{operation_id}",
        ttl,
        json.dumps(safe_data)
    )

def get_cached_operation(redis_client, operation_id: str):
    value = redis_client.get(f"operation:{operation_id}")
    if not value:
        return None
    return json.loads(value)

def invalidate_operation_cache(redis_client, operation_id: str):
    redis_client.delete(f"operation:{operation_id}")

def acquire_operation_lock(redis_client, operation_id: str, ttl: int = 10) -> bool:
    return redis_client.set(
        f"lock:operation:{operation_id}",
        "1",
        nx=True,
        ex=ttl
    )

def release_operation_lock(redis_client, operation_id: str):
    redis_client.delete(f"lock:operaion:{operation_id}")

def find_stuck_operations(db: Session):
    cutoff = datetime.utcnow() - timedelta(seconds=30)

    return db.query(Operation).filter(
        Operation.status == "RUNNING",
        Operation.started_at < cutoff
    ).all()

def recover_stuck_operations(db: Session):
    stuck_ops = find_stuck_operations(db)

    for op in stuck_ops:
        op.status = "FAILED"
        op.updated_at = datetime.utcnow()
        logger.warning(
            "operation_recovered_as_failed",
            extra={
                "operation_id":str(op.id),
                "started_at": op.started_at.isoformat()
            }
        )

    db.commit()
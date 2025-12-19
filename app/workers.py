import time
from sqlalchemy.orm import Session
from .db import SessionLocal
from .crud import update_operation_status, recover_stuck_operations
from .logger import logger
from .metrics import operations_duration_seconds
from .tracing import tracer
from opentelemetry import trace

with operations_duration_seconds.time():
    def execute_operation(operation_id, trace_id):

        with tracer.start_as_current_span(
            "execute_operation",
            context=trace.set_span_in_context(
                trace.NonRecordingSpan(
                    trace.SpanContext(
                        trace_id=trace_id,
                        span_id=0,
                        is_remote=True,
                        trace_flags=trace.TraceFlags(1),
                        trace_state={}
                    )
                )
            )
        ):
            db: Session = SessionLocal()
            try:
                logger.info(
                    "Operation_execution_started",
                    extra={
                        "operation_id": str(operation_id)
                    }
                )
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
    with tracer.start_as_current_span("recover_stuck_operations"):
        db = SessionLocal()
        try:
            recover_stuck_operations(db)
        finally:
            db.close()
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from . import models, schemas, crud
from uuid import UUID


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def get_health():
    return {"Status": "Server is Healthy"}


@app.post("/operations", response_model=schemas.OperationResponse)
def create_operation(
    payload: schemas.OperationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_operation(db, payload.type)

@app.get("/operations/{operation_id}", response_model=schemas.OperationRead)
def read_operation(
    operation_id: UUID,
    db: Session = Depends(get_db)
):
    op = crud.get_operation(db, operation_id)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    return op

@app.patch("/operations/{operation_id}/status", response_model=schemas.OperationRead)
def update_status(
    operation_id: UUID,
    payload: schemas.OperationStatusUpdate,
    idempotency_key: str = Header(..., alias="Idempotency-key"),
    db: Session = Depends(get_db)
):
    try:

        request_hash = crud.hash_request(payload.dict())
        existing = crud.get_idempotent_response(
            db,
            idempotency_key,
            str(operation_id),
            request_hash
        )

        if existing:
            return existing

        result = crud.update_operation_status(
            db, 
            operation_id, 
            payload.status
        )

        crud.save_idempotent_response(
            db,
            idempotency_key,
            str(operation_id),
            request_hash,
            jsonable_encoder(
                schemas.OperationRead.from_orm(result)
            )
        )
        return result
    except ValueError as e:
        if str(e) == "NOT_FOUND":
            raise HTTPException(404, "Operation not found")
        raise HTTPException(400, str(e))

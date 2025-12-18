
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class OperationCreate(BaseModel):
    type: str

class OperationResponse(BaseModel):
    id: UUID
    type: str
    status: str

class OperationRead(BaseModel):
    id: UUID
    type: str
    status: str
    created_at: datetime
    updated_at: datetime

class OperationStatusUpdate(BaseModel):
    status: str
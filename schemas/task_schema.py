from datetime import datetime
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    owner_user: int 
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TaskUpdate(BaseModel):
    title: str
    description: str
    status: str
    priority: str
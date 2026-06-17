from datetime import datetime
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str

class TaskListResponse(BaseModel):
    id: int
    title: str
    status: str
    priority: str

    model_config = {"from_attributes": True}

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
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
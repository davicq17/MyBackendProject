from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class UserResponse(BaseModel):
    id: int
    email:str
    full_name: str
    is_active: bool
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
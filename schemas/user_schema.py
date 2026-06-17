from datetime import datetime
from pydantic import BaseModel

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

class LoginRequest(BaseModel):
    email:str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str ="bearer"
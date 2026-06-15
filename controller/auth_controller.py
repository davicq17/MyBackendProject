from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from schemas.user_schema import UserCreate, UserResponse, Token, LoginRequest
from servicies.auth_service import AuthService

router = APIRouter(prefix="/auth",tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db=db)
    return service.register(user_data)
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db=db)
    return service.login(login_data)
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.user_model import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate, LoginRequest, Token
from utils.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db=db)

    def register(self, user: UserCreate):
        existing_user = self.user_repository.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya esxiste un usuario con ese correo electronico"
            )
        new_user = User(
            email= user.email,
            full_name = user.full_name,
            hashed_password = hash_password(user.password)
        )

        return self.user_repository.create(new_user)
    
    def login(self, login_data: LoginRequest) -> Token:
        user = self.user_repository.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        if not user.is_active: 
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario desactivado"
            )
        access_token = create_access_token(data={"sub":str(user.id)})
        return Token(access_token = access_token )
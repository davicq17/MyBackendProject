from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.user_model import User
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate
from utils.security import hash_password

class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db=db)

    def register(self, user: UserCreate):
        existing_user = self.user_repository.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        new_user = User(
            email= user.email,
            full_name = user.full_name,
            hashed_password = hash_password(user.password)
        )

        return self.user_repository.create(new_user)
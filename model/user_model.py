from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base

class User(Base):
    __tablename__= 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[String] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[String] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[String] = mapped_column(String(255), nullable=False)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    role: Mapped[String] = mapped_column(String(50), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

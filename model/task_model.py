from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base

class Task(Base):
    __tablename__='tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[String] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable= True)
    status: Mapped[String]= mapped_column(String(50), default="pendiente")
    priority: Mapped[String] = mapped_column(String(50), default = "media")
    owner_user: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] =   mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
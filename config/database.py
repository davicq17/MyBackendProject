from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import DATABASES_URL

engine = create_engine(DATABASES_URL)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()
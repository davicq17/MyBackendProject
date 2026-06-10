import os
from dotenv import load_dotenv

load_dotenv()

DATABASES_URL: str = os.getenv("DATABASES","")
SECRET_KEY: str = os.getenv("SECRET_KEY","")
ALGORTHM: str = os.getenv("ALGORITHM","")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",""))
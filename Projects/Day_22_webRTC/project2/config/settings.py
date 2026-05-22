

from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_URL = str(os.getenv("DATABASE_URL"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_EXPIRE_SECONDS = int(os.getenv("REDIS_EXPIRE_SECONDS", 3600))

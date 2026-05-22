from jose import jwt
from datetime import datetime, timedelta, timezone
# from passlib.context import CryptContext
from pwdlib import PasswordHash
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


pwd_hash=PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return pwd_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_hash.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None
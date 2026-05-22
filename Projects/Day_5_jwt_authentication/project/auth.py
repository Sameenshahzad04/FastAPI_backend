from jose import JWTError,jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from database import get_db
from models.user import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from config.config import SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM


#secret key
#algo
#expiration time

#task 3: readme updates----done
#task2:handlerfolder-----db queries----done
#task2:config folder --.env----done

#task 4: alembic migration learning
#task1:uv----study----shift project to uv

#step 1:define jwt 3 thing 


# =OAuth2PasswordBearer(tokenUrl='login')
oauth_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


#this will selects a secure modern hashing algorithm
# step sss
# create var that have hashing algo
# fun verify pwd, get pwd
pwd_hash=PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return pwd_hash.verify(plain_password, hashed_password)


def get_pwd_hash(password):
    return pwd_hash.hash(password)

# create access token
#data is like userid and email 
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # access token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(token:str=Depends(oauth_scheme), db: Session = Depends(get_db)):

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id:int=payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token")

    return user
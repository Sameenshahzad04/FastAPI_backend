from jose import JWTError,jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from database import get_db
from models.user import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from dotenv import load_dotenv
import os
from config.config import SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM
from typing import List

#secret key
#algo
#expiration time

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


# def role_required(required_role: str):
#     def role_checker(current_user: User = Depends(get_current_user)):

#         if current_user.role_name != required_role:
#             raise HTTPException(
#                 status_code=403,
#                 detail="Access denied"
#             )

#         return current_user

#     return role_checker


def role_required(required_roles: str | List[str]):
   
    if isinstance(required_roles, str):
        required_roles = [required_roles]  # Convert string to list

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role_name not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient permissions"
            )
        if current_user.role_name != "super_admin" and not current_user.is_active:
            raise HTTPException(
                status_code=402,
                detail="Account not activated. Payment required."
            )
        return current_user

    return role_checker


def get_org_admin( org_id: int,db: Session=Depends(get_db)):
    return db.query(User).filter(
        User.org_id == org_id,
        User.role_name == "org_admin"
    ).first()

def has_org_admin(db: Session, org_id: int):
    return get_org_admin(db, org_id) is not None











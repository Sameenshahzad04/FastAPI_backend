from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user_schema import UserRegister, UserLogin, Userout,LoginResponse,Token,TokenData
from auth import get_pwd_hash,verify_password,create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from handlers.user_handler import get_user_by_email,create_user,authenticate_user,get_user_by_username
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES

user_routes=APIRouter()





@user_routes.post('/register',response_model=Userout)
def userReg(u:UserRegister,db:Session=Depends(get_db)):

    d_user=get_user_by_email(db,u.email)
    if d_user:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="user already register")
    hashed_password = get_pwd_hash(u.password)
    
    return create_user(db,u.username,u.email,hashed_password)

# Users can login

@user_routes.post('/login',response_model=Token)
def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)):

    d_user = authenticate_user(db,form_data.username,form_data.password)
   
    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"id": d_user.id, "username": d_user.username},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message":"User is now logged in successfully"

    }
   
    
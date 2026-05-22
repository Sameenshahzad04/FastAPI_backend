from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user_schema import UserRegister, UserLogin, Userout,LoginResponse
from typing import Dict

r=APIRouter()

@r.post('/register',response_model=Userout)
def userReg(u:UserRegister,db:Session=Depends(get_db)):

    d_user=db.query(User).filter(User.email==u.email).first()
    if d_user:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="user already register")
    n_user = User(
        username=u.username,
        email=u.email,
        password=u.password
    )
    db.add(n_user)
    db.commit()
    db.refresh(n_user)
    return n_user

# Users can login

@r.post('/login',response_model=LoginResponse)
def user_login(u:UserLogin,db:Session=Depends(get_db)):

    d_user=db.query(User).filter( User.email==u.email and User.password==u.password).first()
    
    if not d_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user is not  register")
   
    return LoginResponse( message="User is now logged in successfully",user=d_user  )
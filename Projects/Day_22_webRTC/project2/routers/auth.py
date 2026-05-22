from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.auth_schema import UserRegister, UserLogin, Token, UserOut
from handlers.auth_handler import register_user, login_user

r = APIRouter()

@r.post("/register", response_model=UserOut)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user_data.username, user_data.email, user_data.password)

@r.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, login_data.username, login_data.password)
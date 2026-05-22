from fastapi import APIRouter, Depends, HTTPException,status,Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user_schema import UserRegister, Userout,LoginResponse,Token,TokenData
from schemas.page import Page
from jwt import get_pwd_hash,verify_password,create_access_token,role_required
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from handlers.user_handler import deleteOrganization, get_user_by_email,create_user,authenticate_user,show_all_users,delete_user,createOrganization,showOrganization
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.organization_schema import organizationDetails,organizationin

user_routes=APIRouter()

#user can register and login 
#admin create user by go to regiester,delete user,show all users



@user_routes.post('/register',response_model=Userout)
def userReg(u:UserRegister,db:Session=Depends(get_db),current_user: User = Depends(role_required("admin"))):

    d_user=get_user_by_email(db,u.email)
    if d_user:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="user already register")
    hashed_password = get_pwd_hash(u.password)
    
    return create_user(db,hashed_password,u,current_user)

# Users can login

@user_routes.post('/login',response_model=Token)
def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)):

    d_user = authenticate_user(db,form_data.username,form_data.password)
   
    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"id": d_user.id, "username": d_user.username,"role":d_user.role_name},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message":"User is now logged in successfully"

    }
   
# #for manager to see all team leads
# @user_routes.get("/team_leads",response_model=list[Userout])
# def show_team_leads(db: Session = Depends(get_db), current_user: User = Depends(role_required("manager"))):
   
#     return get_team_leads(db)
#get all dev for team lead 
# @user_routes.get("/developers",response_model=list[Userout])
# def get_developers(db: Session = Depends(get_db), current_user: User = Depends(role_required("team_lead"))):
    
#     return show_developers(db)



#fun for admin
#create user by registering them
#delete user

#for admin to see all users
@user_routes.get("/users",response_model=Page[Userout])
def show_users(db: Session = Depends(get_db), current_user: User = Depends(role_required("admin")),
               search: str = Query(None, description="Search by username or email"),
               page: int = Query(1, ge=1,description="page number"),
               no_records: int = Query(5, description="number of records per page")
               
               ):
   
    return show_all_users(db, page, no_records, search)


@user_routes.delete("/delete_user/{u_id}")
def deleting_user(u_id:int,db: Session = Depends(get_db), current_user: User = Depends(role_required("admin"))):

    return delete_user(db,u_id)

@user_routes.post('/organization',response_model=organizationDetails)
def create_organization(org:organizationin,db: Session = Depends(get_db), current_user: User = Depends(role_required("admin"))):

    return createOrganization(db,org,current_user)

@user_routes.get('/show_organization',response_model=list[organizationDetails])
def show_organization(db: Session = Depends(get_db), current_user: User = Depends(role_required("admin"))):
   

    return showOrganization(db)

@user_routes.delete('/delete_organization/{d_id}')
def delete_organization(d_id:int,db: Session = Depends(get_db)):



    return deleteOrganization(db,d_id)

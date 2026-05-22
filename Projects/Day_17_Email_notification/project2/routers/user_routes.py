from fastapi import APIRouter, Depends, HTTPException,status,Query
from sqlalchemy.orm import Session
import stripe
from models.organization import Organization
from database import create_org_schema, get_db
from models.user import User
from schemas.user_schema import UserRegister, Userout,LoginResponse,Token,TokenData, Userupdate
from schemas.page import Page
from jwt import get_pwd_hash,verify_password,create_access_token,role_required
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from handlers.user_handler import deleteOrganization, get_user_by_email,create_user,authenticate_user,show_all_users,delete_user,createOrganization,showOrganization,get_price_id, update_user, updateOrganization
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.organization_schema import organizationDetails,organizationin,organizationUpdate

user_routes=APIRouter()

# d_user can register and login 
# admin create d_user by go to regiester,delete d_user,show all users

# to create super-admin

# @user_routes.post('/register',response_model=Userout)
# def userReg(u:UserRegister,db:Session=Depends(get_db)):

#     d_user=get_user_by_email(db,u.email)
#     if d_user:
#         raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="d_user already register")
#     hashed_password = get_pwd_hash(u.password)
    
#     return create_user(db,hashed_password,u)





@user_routes.post('/register',response_model=Userout)
def userReg(u:UserRegister,db:Session=Depends(get_db),current_user: User = Depends(role_required(["super_admin", "org_admin"]))):

    d_user=get_user_by_email(db,u.email)
    if d_user:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="d_user already register")
    hashed_password = get_pwd_hash(u.password)
    
   
    return  create_user(db,hashed_password,u,current_user)

#login routes
@user_routes.post('/login', response_model=Token)
def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
# Authenticating user using jwt form
    d_user = authenticate_user(db, form_data.username, form_data.password)


# to check first time login of user and not super_admin  then to activate subscription
    if d_user.role_name != "super_admin" and not d_user.first_login_done:
        try:

#  Creating stripe  Customer + attach test card to customer + create subscription for user
            customer = stripe.Customer.create(
                email=d_user.email,
                name=d_user.username,
                payment_method=d_user.stripe_payment_method_id ,
                invoice_settings={
                    "default_payment_method": "pm_card_visa"
                },
                metadata={"user_id": d_user.id, "org_id": d_user.org_id}
            )

            
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": get_price_id(d_user.pricing_plan)}],
                expand=["latest_invoice.payment_intent"] 
            )

# Updating user data in DB
            d_user.first_login_done = True
            d_user.is_active = True
            d_user.stripe_customer_id = customer.id
            d_user.stripe_subscription_id = subscription.id
            d_user.stripe_payment_method_id = d_user.stripe_payment_method_id#"pm_card_visa"  # Save for reference
            db.commit()
            db.refresh(d_user)

        except stripe.error.CardError as e:
            db.rollback()
            raise HTTPException(400, f"Card error: {e.user_message}")
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Payment setup failed: {str(e)}")

# Generating JWT token for access
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"id": d_user.id, "username": d_user.username, "role": d_user.role_name},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "User is now logged in successfully"
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
#create d_user by registering them
#delete d_user

#for admin to see all users
@user_routes.get("/users",response_model=Page[Userout])
def show_users(db: Session = Depends(get_db), current_user: User = Depends(role_required(["super_admin", "org_admin"])),
               search: str = Query(None, description="Search by username or email"),
               page: int = Query(1, ge=1,description="page number"),
               no_records: int = Query(5, description="number of records per page")
               
               ):
   
    return show_all_users(db, page, no_records, search,current_user)
@user_routes.put("/update_user/{u_id}",response_model=Userupdate)
def updating_user(u_id:int, u:Userupdate,db: Session = Depends(get_db), current_user: User = Depends(role_required(["super_admin", "org_admin"]))):

    return update_user(db,current_user,u_id,u)  

@user_routes.delete("/delete_user/{u_id}")
def deleting_user(u_id:int,db: Session = Depends(get_db), current_user: User = Depends(role_required(["super_admin", "org_admin"]))):

    return delete_user(db,current_user,u_id)

@user_routes.post('/organization',response_model=organizationDetails)
def create_organization(org:organizationin,db: Session = Depends(get_db), current_user: User = Depends(role_required("super_admin"))):


    new_org = createOrganization(db, org, current_user)
    
    # CREATE SEPARATE SCHEMA FOR THIS ORG
    create_org_schema(new_org.id)
    
    return new_org

@user_routes.post('/update_organization',response_model=organizationDetails)
def update_organization(org:organizationUpdate,db: Session = Depends(get_db), current_user: User = Depends(role_required("super_admin"))):

    return updateOrganization(db,org,current_user)

@user_routes.get('/show_organization',response_model=list[organizationDetails])
def show_organization(db: Session = Depends(get_db), current_user: User = Depends(role_required("super_admin"))):
   

    return showOrganization(db)

@user_routes.delete('/delete_organization/{d_id}')
def delete_organization(d_id:int,db: Session = Depends(get_db)):



    return deleteOrganization(db,d_id)
# @user_routes.post('/organization/{org_id}/admin', response_model=Userout)
# def create_org_admin(
#     org_id: int,
#     user_data: UserRegister,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(role_required("super_admin"))
# ):
#     """Super Admin creates org_admin for an organization"""
    
#     # Check org exists
#     org = db.query(Organization).filter(Organization.id == org_id).first()
#     if not org:
#         raise HTTPException(status_code=404, detail="Organization not found")
    
#     # Check if org already has admin
#     existing = db.query(User).filter(
#         User.org_id == org_id,
#         User.role_name == "org_admin"
#     ).first()
    
#     if existing:
#         raise HTTPException(status_code=400, detail="Org already has admin")
    
#     # Create org_admin user
#     hashed_password = get_pwd_hash(user_data.password)
    
#     new_user = User(
#         username=user_data.username,
#         email=user_data.email,
#         password=hashed_password,
#         role_name="org_admin",
#         org_id=org_id,
#         is_active=True,
#         first_login_done=True
#     )
    
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
    
#     return new_user



#aadmin can see payment status of all users and org admin can see payment status of users in their org

@user_routes.get("/payment-status", response_model=dict)
def get_payment_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["super_admin", "org_admin"]))
):
   
    if current_user.role_name.lower() == "super_admin":
        users = db.query(User).filter(User.role_name != "super_admin").all()
    else:
        users = db.query(User).filter(User.org_id == current_user.org_id).all()
    
    payment_status = []
    for user in users:
        payment_status.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role_name,
            "is_active": user.is_active,
            "pricing_plan": user.pricing_plan,
            "stripe_customer_id": user.stripe_customer_id,
            "stripe_subscription_id": user.stripe_subscription_id,
            "first_login_done": user.first_login_done
        })
    
    return {
        "total_users": len(users),
        "active_subscriptions": sum(1 for u in payment_status if u["is_active"]),
        "pending_activation": sum(1 for u in payment_status if not u["first_login_done"]),
        "users": payment_status
    }
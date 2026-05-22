# handlers/user_handler.py

import stripe
from config.config import STRIPE_SECRET_KEY
from sqlalchemy.orm import Session
from fastapi import HTTPException, status,BackgroundTasks
from models.user import User
from jwt import verify_password
from models.organization import Organization

from utils.email_service import send_credentials_email
import logging

logger = logging.getLogger(__name__)

#  Stripe key
stripe.api_key = STRIPE_SECRET_KEY

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_price_id(plan: str) -> str:
    prices = {
        "basic": "price_1T9MvhGn7y3nRRWTZYkVzkak", 
        "pro": "price_1T9My6Gn7y3nRRWTak0xlrZO"
    }
    return prices.get(plan)
   




def create_user(db: Session, hashed_password: str,u:User,cur_user:User):
    


    existing = db.query(User).filter(User.email == u.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if u.org_id:
        org = db.query(Organization).filter(Organization.id == u.org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
    
    user_role=cur_user.role_name.lower()
    if user_role in ["super_admin"]:

      
       if u.role_name.lower() == "org_admin":
            existing_org_admin = db.query(User).filter(
            User.org_id == u.org_id,
            User.role_name == "org_admin").first()

            if existing_org_admin:
                raise HTTPException(
                status_code=400,
                detail=f"Organization with ID {u.org_id} already has an admin: {existing_org_admin.username}"
                )


            new_user = User(
            username=u.username,
                email=u.email,
                password=hashed_password,
                role_name=u.role_name.lower(),
                org_id=u.org_id,
                stripe_payment_method_id=u.stripe_payment_method_id,
                pricing_plan=u.pricing_plan,
                is_active=False,  #  active on first login
                first_login_done=False
            )
       else: 
            if not u.org_id:
                raise HTTPException(status_code=400, detail="org_id required for user")
            new_user = User(
                username=u.username,
                email=u.email,
                password=hashed_password,
                role_name="user",
                org_id=u.org_id,
                stripe_payment_method_id=u.stripe_payment_method_id,
                pricing_plan=u.pricing_plan,
                is_active=False,
                first_login_done=False
            )
         
    elif user_role in ["org_admin"]:

        if u.org_id != cur_user.org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only create users within your organization")
        if u.role_name.lower() != "user":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Org admins can only create users with the 'user' role")
        new_user = User(
        username=u.username,
        email=u.email,
        password=hashed_password,
        role_name=u.role_name.lower(),
        org_id=cur_user.org_id,
        stripe_payment_method_id=u.stripe_payment_method_id,
        pricing_plan=u.pricing_plan,
        is_active=False, 
        first_login_done=False
         )
          
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
       # Send email
    if org :
         try:
                send_credentials_email(
                    to=u.email,
                    username=u.username,
                    password=u.password,
                    org_name=org.name
                )
                logger.info(f"📧 Email sent to {u.email}")
         except Exception as e:
                logger.warning(f"Email failed to send to {u.email}: {str(e)}")
    
   
    return new_user
    


def delete_user(db: Session, user: User,u_id:int):
    if user.role_name.lower() == "org_admin":
        if user.org_id != get_user_by_id(db,u_id).org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete users within your organization")
        if get_user_by_id(db,u_id).role_name.lower() != "user":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Org admins can only delete users with the 'user' role")
    user = get_user_by_id(db, u_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"message": f"User with ID {u_id} deleted successfully"}


def update_user(db: Session, user: User,u_id:int, u:User):
    if u_id<=1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update super admin")
    if user.role_name.lower() == "org_admin":
        if user.org_id != get_user_by_id(db,u_id).org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update users within your organization")
        if get_user_by_id(db,u_id).role_name.lower() != "user":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Org admins can only update users with the 'user' role")
    elif user.role_name.lower() == "super_admin":
        if u.role_name.lower() == "org_admin":
            existing_org_admin = db.query(User).filter(
            User.org_id == u.org_id,
            User.role_name == "org_admin").first()

            if existing_org_admin and existing_org_admin.id != u_id:
                raise HTTPException(
                status_code=400,
                detail=f"Organization with ID {u.org_id} already has an admin: {existing_org_admin.username}"
                )



    db_user = get_user_by_id(db, u_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db_user.username = u.username
    db_user.email = u.email
    db_user.org_id = u.org_id
    db_user.role_name = u.role_name
    db_user.stripe_payment_method_id = u.stripe_payment_method_id
    db_user.pricing_plan = u.pricing_plan

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not registered"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )

    return user
def show_all_users(db: Session, page: int, no_records: int,search:str,current_user: User):
    
    if current_user.role_name.lower() == "super_admin":
        users = db.query(User)
    else:
        users = db.query(User).filter(User.org_id == current_user.org_id)
    
    if search:
        users = users.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    
    total = users.count()  # Get total count before pagination

    
    start = (page - 1) * no_records

    if start >= total:
            raise HTTPException(status_code=404, detail="Page out of range")
    end = start + no_records


    # Slice the data
    if total>=no_records:
       
        paginated_data = users[start:end]
    else:
         paginated_data = users

    
    pages = (total + no_records - 1) // no_records

    if page > pages:
        raise HTTPException(status_code=404, detail="Page out of range")

    return {
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
        "data": paginated_data
    }

def createOrganization(db: Session, org,current_user: User):

      
    new_org = Organization(
        name=org.name,
        des=org.des,
        owner_id=org.owner_id

    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org  

def showOrganization(db: Session ):

    o=db.query(Organization).all()
    return o

def deleteOrganization(db: Session, id: int):
    o = db.query(Organization.id==id)
    if not o:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="organization id not found"
        )
    db.delete(o)
    db.commit()
    return {"message": f"User with ID {id} deleted successfully"}

def updateOrganization(db: Session, org,current_user: User):

      db_org=db.query(Organization).filter(Organization.id==org.id).first()
      if not db_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="organization id not found"
        )
   
      db_org.id=org.id,
      db_org.name=org.name,
      db_org.des=org.des,
      db_org.owner_id=org.owner_id

   
      db.add(db_org)
      db.commit()
      db.refresh(db_org)
      return db_org  


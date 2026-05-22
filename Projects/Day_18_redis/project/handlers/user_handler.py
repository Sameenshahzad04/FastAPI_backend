# handlers/user_handler.py

import stripe
from config.config import STRIPE_SECRET_KEY
from sqlalchemy.orm import Session
from fastapi import HTTPException, status,BackgroundTasks
from models.user import User
from jwt import verify_password
from models.organization import Organization
from utils.redis_service import cache_get, cache_set, cache_delete

from utils.email_service import send_credentials_email
import logging

logger = logging.getLogger(__name__)

#  Stripe key
stripe.api_key = STRIPE_SECRET_KEY

def get_user_by_email(db: Session, email: str):

   
    
    # Check cache first
    
    cached = cache_get(f"user_email:{email}")
    
    if cached:
        print(f"Cache hit: {email}")
        return User(**cached)
    
    # Cache miss - query database
    print(f"Cache miss: {email}")
    user = db.query(User).filter(User.email == email).first()
    
    # Cache the result (10 minutes)
    if user:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role_name": user.role_name
        }
        cache_set(f"user_email:{email}", user_dict, expire_seconds=600)
    
    return user


  


def get_user_by_username(db: Session, username: str):


    
 
    cached = cache_get(f"user_name:{username}")
    
    if cached:
        print(f" Cache hit: {username}")
        return User(**cached)
    
    # Cache miss - query database
    print(f" Cache miss: {username}")
    user = db.query(User).filter(User.username == username).first()
    
    # Cache the result (10 minutes)
    if user:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "role_name": user.role_name,
            "org_id": user.org_id,
            "stripe_payment_method_id": user.stripe_payment_method_id,
            "pricing_plan": user.pricing_plan,
            "is_active": user.is_active,
            "first_login_done": user.first_login_done,
            "stripe_customer_id": user.stripe_customer_id,
            "stripe_subscription_id": user.stripe_subscription_id
        }
        cache_set(f"user_name:{username}", user_dict, expire_seconds=600)
    
    return user





def get_user_by_id(db: Session, user_id: int):

    
    
    # Check cache first
   
    cached = cache_get(f"user_id:{user_id}")
    
    if cached:
        print(f" Cache hit: {user_id}")
        return User(**cached)
    
    # Cache miss - query database
    print(f" Cache miss: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    # Cache the result (10 minutes)
    if user:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role_name": user.role_name,
            "org_id": user.org_id

        }
        cache_set(f"user_id:{user_id}", user_dict, expire_seconds=600)
    
    return user
def get_user_by_org_id(db: Session, org_id: int):

   
    user = db.query(User).filter(User.org_id == org_id)
  
    return user



def get_org_by_id(db: Session, org_id: int):
    """Get organization by ID"""
      # Check cache first
    # cache_key = CacheKeys.org_id(org_id)
    cached = cache_get(f"org_id:{org_id}")
    
    if cached:
        print(f" Cache hit: {org_id}")
        return Organization(**cached)
    
    # Cache miss - query database
    print(f" Cache miss: {org_id}")
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    # Cache the result (10 minutes)
    if org:
        org_dict = {
            "id": org.id,
           
            "name": org.name,
            "des": org.des,
            "owner_id": org.owner_id   


        }
        cache_set(f"org_id:{org_id}", org_dict, expire_seconds=600)
    
    return org



def get_org_admin_by_rolename(db: Session, org_id: int, role_name: str):


    cached=cache_get(f"org_admin:{org_id}")
    if cached:
        print(f" Cache hit: {org_id}")
        return User(**cached)
    
     # Cache miss - query database
    print(f" Cache miss: {org_id}")
    org_admin = db.query(User).filter(
        User.org_id == org_id,
        User.role_name == role_name
    ).first()
    # Cache the result (10 minutes)
    if org_admin:
        user_dict = {
            "id": org_admin.id,
            "username": org_admin.username,
            "email": org_admin.email,
            "role_name": org_admin.role_name
        }
        cache_set(f"org_admin:{org_id}", user_dict, expire_seconds=600)

    return org_admin    
            

def invalidate_user_cache(user_id, email):
    """Clear user cache"""
    cache_delete(f"user_id:{user_id}")
    cache_delete(f"user_email:{email}")

def get_price_id(plan: str) -> str:
    prices = {
        "basic": "price_1T9MvhGn7y3nRRWTZYkVzkak", 
        "pro": "price_1T9My6Gn7y3nRRWTak0xlrZO"
    }
    return prices.get(plan)
   




def create_user(db: Session, hashed_password: str,u:User,cur_user:User):
    


    existing_mail = get_user_by_email(db, u.email)
    existing_username = get_user_by_username(db, u.username)
    if existing_mail:
        raise HTTPException(status_code=400, detail="Email already registered")
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    if u.org_id:
        org = get_org_by_id(db, u.org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
    
    user_role=cur_user.role_name.lower()
    if user_role in ["super_admin"]:

      
       if u.role_name.lower() == "org_admin":
            existing_org_admin = get_org_admin_by_rolename(db, u.org_id, "org_admin")   

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
                logger.info(f" Email sent to {u.email}")
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

def show_all_users(db: Session, page: int, no_records: int, search: str, current_user: User):
    
    
    # Create dynamic cache key
    cache_key = f"users:{current_user.role_name.lower()}:{current_user.org_id or 'all'}:page:{page}:size:{no_records}"
    
    if search:
        cache_key += f":search:{search}"
    
    # Check cache first
    cached = cache_get(cache_key)
    
    if cached:
        logger.info(f"Cache hit: {cache_key}")
        return cached 
    
    
    logger.info(f" Cache miss: {cache_key}")
    
    # Build query based on role
    if current_user.role_name.lower() == "super_admin":
        users_query = db.query(User)
    else:
        users_query = get_user_by_org_id(db, current_user.org_id)
        
    
    # Apply search filter
    if search:
        users_query = users_query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    #  Get total count BEFORE pagination (Query object method)
    #count work with SqlAlchemy query object and does a fast COUNT(*) in the database
    #count does not work with lists or already executed queries, it must be called on the Query object before .all() or .first()
    total = users_query.count()
    
    if total == 0:
        result = {
            "page": page,
            "records": no_records,
            "total": 0,
            "pages": 0,
            "data": []
        }
        cache_set(cache_key, result, expire_seconds=300)
        return result
    
    # Calculate pages
    pages = (total + no_records - 1) // no_records
    
    if page > pages:
        raise HTTPException(status_code=404, detail="Page out of range")
    
    #  Apply pagination and execute query (returns LIST of User objects)
    start = (page - 1) * no_records
    paginated_users = users_query.offset(start).limit(no_records).all()
    
    #  Convert SQLAlchemy User objects to dictionaries matching Userout schema
    # Userout has: id, username, email, org_id
    users_data = []
    for user in paginated_users:
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "org_id": user.org_id
        })
    
    #  Build complete response matching Page[Userout] schema
    result = {
        "page": page,
        "records": no_records,
        "total": total,
        "pages": pages,
        "data": users_data  # List of dicts matching Userout
    }
    
    #  Cache the complete result (10 minutes)
    cache_set(cache_key, result, expire_seconds=600)
    logger.info(f" Cached: {cache_key}")
    
    return result

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
    cached = cache_get("orgs:all")
    if cached:
        logger.info(f" Cache hit: orgs:all")
        return cached
    
    logger.info(f" Cache miss: orgs:all")
    orgs = db.query(Organization).all()
    
    # Convert to dict for caching using list comprehension
    orgs_data = [
        {
            "id": o.id,
            "name": o.name,
            "des": o.des,
            "owner_id": o.owner_id
        }
        for o in orgs
    ]
    
    cache_set("orgs:all", orgs_data, expire_seconds=600)
    logger.info(f" Cached: orgs:all")
    
    return orgs_data


def deleteOrganization(db: Session, id: int):
    o = get_org_by_id(db, id)
    if not o:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="organization id not found"
        )
    db.delete(o)
    db.commit()
    return {"message": f"User with ID {id} deleted successfully"}

def updateOrganization(db: Session, org,current_user: User):

      db_org=get_org_by_id(db, org.id)
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


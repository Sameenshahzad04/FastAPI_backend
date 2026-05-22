# handlers/user_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from jwt import verify_password
from models.organization import Organization


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, hashed_password: str,u:User,cur_user:User):
    
    user_role=cur_user.role_name.lower()
    # if user_role not in ["admin"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid role. Must be 'admin'."
    #     )    
    new_user = User(
        username=u.username,
        email=u.email,
        password=hashed_password,
        role_name=user_role,
        org_id=u.org_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"message": f"User with ID {user_id} deleted successfully"}



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
def show_all_users(db: Session, page: int, no_records: int):
    users = db.query(User).all()

    
    total = len(users)

    
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
        owner_id=current_user.id

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


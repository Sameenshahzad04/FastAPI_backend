# handlers/project_handler.py

# from asyncio import Task

from models.task import Task
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models.project import Project
from models.user import User

def create_project(db: Session, name: str, des: str, owner_id: int):
    proj = Project(
        name=name,
        des=des,
        owner_id=owner_id
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


def get_user_projects(db: Session, user: User, page: int, no_records: int,search:str):
  
    
    # Returns projects based on user role:
    # -Manager: projects they created (owner_id)
    #  Team Lead: projects assigned to them (assigned_to)
    
    # if user.role_name == "admin":
        # Manager sees projects he owns
        # projects = db.query(Project).filter(Project.owner_id == user.id).all()
    projects =db.query(Project).options(
            joinedload(Project.tasks)
            .joinedload(Task.assigned_user)
        ).filter(Project.owner_id == user.id)
        

    if search:
         projects = projects.filter(
            (Project.name.ilike(f"%{search}%")) 
            
        )
    total =     projects.count()  # Get total count before pagination
    start = (page - 1) * no_records

    if start >= total:
            raise HTTPException(status_code=404, detail="Page out of range")
    end = start + no_records
    # Slice the data
    if total>=no_records:
       
        paginated_data = projects[start:end]
    else:
         paginated_data = projects

    
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
        
    # else:
    #     # Team Lead sees projects assigned to him
    #     projects = db.query(Project).filter(Project.assigned_to == user.id).all()
    


def get_single_project(db: Session, project_id: int, user: User):
   
    if user.role_name == "admin":
             proj = db.query(Project).options(
            joinedload(Project.tasks)
            .joinedload(Task.assigned_user)
            ).filter(Project.id == project_id, Project.owner_id == user.id).first()
    # elif user.role_name == "user":
    #     proj = db.query(Project).filter(
    #         Project.id == project_id,
    #         Project.assigned_to == user.id
    #     ).first()
    else:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=f"project {project_id} not found or unauthorized"
       )
    return proj


def delete_project(db: Session, project_id: int, user: User):
    proj = get_single_project(db, project_id, user)

    db.delete(proj)
    db.commit()
    return {"msg": f"project {project_id} is deleted"}

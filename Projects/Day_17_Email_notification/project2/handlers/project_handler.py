

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from models.organization import Organization
from models.task import Task
from models.project import Project
from models.user import User
# from sqlalchemy import text

def create_project(db: Session,p:Project,user: User):
    
    proj = Project(
        name=p.name,
        des=p.des,
        owner_id=user.id,
        org_id=user.org_id
    )
     
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj
# def create_project(p:Project,user: User):
    
#     # owner = db.query(User).filter(User.id == user.id).first()
#     # if not owner:
#     #     raise HTTPException(status_code=404, detail="Owner not found")
#     if user.role_name == "org_admin":
#           proj = Project(
#         name=p.name,
#         des=p.des,
#         owner_id=user.id,
#         org_id=user.org_id
#         )
#     else:
        
#         proj = Project(
#         name=p.name,
#         des=p.des,
#         owner_id=user.id,
#         org_id=p.org_id
#         )
   
#     db.add(proj)
#     db.commit()
#     db.refresh(proj)
#     return proj

def get_user_projects(db: Session, user: User, page: int, no_records: int,search:str):
  
      # elif user.role_name == "super_admin":
    if user.role_name == "super_admin":
        # Query all projects (not raw SQL)
        projects = db.query(Project).options(
            joinedload(Project.tasks).joinedload(Task.assigned_user)
        )
    else:
        # Filter by org_id
        projects = db.query(Project).filter(
            Project.org_id == user.org_id
        ).options(
            joinedload(Project.tasks).joinedload(Task.assigned_user)
        )
    

    if search:
         projects = projects.filter(
            (Project.name.ilike(f"%{search}%")) 
            
        )
    total = projects.count() 
    start = (page - 1) * no_records

    # if start >= total:
    #         raise HTTPException(status_code=404, detail="Page out of range")
    # end = start + no_records
    # # Slice the data
    # if total>=no_records:
       
    #     paginated_data = projects[start:end]
    # else:
    #      paginated_data = projects

    
    # pages = (total + no_records - 1) // no_records
    if start >= total and total > 0:
        raise HTTPException(status_code=404, detail="Page out of range")
    
    paginated_data = projects.offset(start).limit(no_records).all()
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
   
    # if user.role_name == "super_admin":
    #          proj = db.query(Project).options(
    #         joinedload(Project.tasks)
    #         .joinedload(Task.assigned_user)
    #         ).filter(Project.id == project_id, Project.owner_id == user.id).first()
    # elif user.role_name == "org_admin":
    #     projects =db.query(Project).options(
    #         joinedload(Project.tasks)
    #         .joinedload(Task.assigned_user)
    #     ).filter(Project.owner_id == user.id,Project.org_id == user.org_id).first()
    # else:
    #    raise HTTPException(
    #        status_code=status.HTTP_404_NOT_FOUND,
    #        detail=f"project {project_id} not found or unauthorized"
    #    )
    # return proj
    project = db.query(Project).filter(Project.id == id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


def delete_project(db: Session, project_id: int, user: User):
   
    # if user.role_name == "org_admin":
    #     proj = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    # else:
    #     proj = get_single_project(db, project_id, user)

    # db.delete(proj)
    # db.commit()
    # return {"msg": f"project {project_id} is deleted"}
    project = db.query(Project).filter(Project.id == id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted"}
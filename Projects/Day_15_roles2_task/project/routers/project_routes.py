from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from models.user import User
from schemas.project_schema import Projectinfo,Projectfind,Projectin
from jwt import get_current_user,role_required
from handlers.project_handler import create_project,get_single_project,get_user_projects,delete_project
from handlers.user_handler import get_user_by_id
project_routes=APIRouter()


#admin can create,delete project and assign to user
#user can only see project assigned to him

# Each project can have tasks
# # Tasks belong to a project
# pOST /projects
# GET /projects
# GET /projects/{id}
# DELETE /projects/{id}

@project_routes.post('/',response_model=Projectinfo)
def createProject(p:Projectin,user:User=Depends(role_required("admin")), d : Session=Depends(get_db)):

   
    return create_project(d,p.name,p.des,user.id)

@project_routes.get('/',response_model=list[Projectinfo])
def Show_Projects(user:User=Depends(get_current_user), d : Session=Depends(get_db)):

  
    proj=get_user_projects(d,user)
    
    return proj


@project_routes.get('/{id}',response_model=Projectinfo)
def Show_single_Projects(id:int,u:User=Depends(get_current_user), d : Session=Depends(get_db)):

  
   proj=get_single_project(d,id,u)
   if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
   return proj

@project_routes.delete('/{id}')
def Del_Projects(id:int,u:User=Depends(role_required("admin")), d : Session=Depends(get_db)):

   
   return delete_project(d,id,u)

@project_routes.post('/assign/{project_id}/user/{user_id}',response_model=Projectinfo)
def assign_project_to_user(project_id: int, user_id: int, db: Session = Depends(get_db),assigner:User=Depends(role_required("admin"))):
   
    project = get_single_project(db, project_id, assigner)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    user =get_user_by_id(db, user_id)   
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    
    if  user.role_name != "user":
        raise HTTPException(status_code=403, detail="Project can only be assigned to normal users")
    

    project.assigned_to = user_id
    db.commit()
    db.refresh(project)
    return project
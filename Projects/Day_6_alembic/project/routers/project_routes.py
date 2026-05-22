from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from models.user import User
from schemas.project_schema import Projectinfo,Projectfind
from security import get_current_user
from handlers.project_handler import create_project,get_single_project,get_user_projects,delete_project

project_routes=APIRouter()


# Each project can have tasks
# # Tasks belong to a project
# pOST /projects
# GET /projects
# GET /projects/{id}
# DELETE /projects/{id}

@project_routes.post('/',response_model=Projectinfo)
def createProject(p:Projectfind,user:User=Depends(get_current_user), d : Session=Depends(get_db)):

    
   
    return create_project(d,p.name,p.des,user.id)

@project_routes.get('/',response_model=list[Projectinfo])
def Show_Projects(user:User=Depends(get_current_user), d : Session=Depends(get_db)):

  
    proj=get_user_projects(d,user.id)
    
    return proj


@project_routes.get('/{id}',response_model=Projectinfo)
def Show_Projects(id:int,u:User=Depends(get_current_user), d : Session=Depends(get_db)):

  
   proj=get_single_project(d,id,u.id)
   if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
   return proj

@project_routes.delete('/{id}')
def Del_Projects(id:int,u:User=Depends(get_current_user), d : Session=Depends(get_db)):

   
   return delete_project(d,id,u.id)
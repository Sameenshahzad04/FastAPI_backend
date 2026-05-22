from fastapi import APIRouter, Depends, HTTPException,status,Query
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from schemas.project_schema import Projectinfo,Projectfind,Projectget

ro=APIRouter()


# Each project can have tasks
# # Tasks belong to a project
# pOST /projects
# GET /projects
# GET /projects/{id}
# DELETE /projects/{id}

@ro.post('/',response_model=Projectinfo)
def createProject(p:Projectfind, d : Session=Depends(get_db)):

    proj = Project(
        name=p.name,
        des=p.des,
        owner_id=p.owner_id
    )
    
    d.add(proj)
    d.commit()
    d.refresh(proj)
    return proj

@ro.get('/',response_model=list[Projectinfo])
def Show_Projects(owner_id: int = Query(..., description="ID of the project owner"), d : Session=Depends(get_db)):

    proj = d.query(Project).filter(Project.owner_id==owner_id).all()

    return proj
@ro.get('/{id}',response_model=Projectinfo)
def Show_Projects(id:int, d : Session=Depends(get_db)):

   proj = d.query(Project).filter(Project.id == id).first()
   if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
   return proj

@ro.delete('/{id}')
def Del_Projects(id:int, d : Session=Depends(get_db)):

   proj = d.query(Project).filter(Project.id == id).first()
   if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
   d.delete(proj)
   d.commit()
   return {"msg":f"project {id} is deleted "}
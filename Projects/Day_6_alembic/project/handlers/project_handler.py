# handlers/project_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.project import Project


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


def get_user_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.owner_id == user_id).all()


def get_single_project(db: Session, project_id: int, user_id: int):
    proj = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user_id
    ).first()

    
    return proj


def delete_project(db: Session, project_id: int, user_id: int):
    proj = get_single_project(db, project_id, user_id)

    db.delete(proj)
    db.commit()
    return {"msg": f"project {project_id} is deleted"}

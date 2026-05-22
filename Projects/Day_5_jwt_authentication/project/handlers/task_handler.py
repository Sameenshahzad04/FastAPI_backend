# handlers/task_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.task import Task
from models.project import Project


def create_task(db: Session, title: str, des: str, status_value: str, project_id: int, user_id: int):

    proj = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user_id
    ).first()

    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    new_task = Task(
        title=title,
        des=des,
        status=status_value,
        project_id=project_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_project_tasks(db: Session, project_id: int, user_id: int):

    proj = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user_id
    ).first()

    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )

    tasks = db.query(Task).filter(Task.project_id == project_id).all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found"
        )

    return tasks


def update_task(db: Session, task_id: int, user_id: int, title: str, des: str, status_value: str):

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )

    task.title = title
    task.des = des
    task.status = status_value

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, user_id: int):

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )

    db.delete(task)
    db.commit()

    return {"msg": f"task {task_id} deleted"}

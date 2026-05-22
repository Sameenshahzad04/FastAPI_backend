# handlers/task_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from schemas.task_schema import tasks,tasksIn
from models.task import Task
from models.project import Project
from models.user import User

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


def get_project_tasks(db: Session, project_id: int, user:User):

    if user.role_name=="admin":

        tasks = db.query(Task).filter(Task.project_id == project_id).all()
    else:
        tasks = db.query(Task).filter(Task.project_id == project_id, Task.assigned_to == user.id).all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found"
        )

    return tasks


def update_task(db: Session, task_id: int, user: User,t:tasksIn):

    if user.role_name=="admin":
        task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user.id
        ).first()
    else:
        task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Task.assigned_to == user.id
        ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )

    task.title = t.title
    task.des = t.des
    task.status = t.status

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, user: User):

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )

    db.delete(task)
    db.commit()

    return {"msg": f"task {task_id} deleted"}

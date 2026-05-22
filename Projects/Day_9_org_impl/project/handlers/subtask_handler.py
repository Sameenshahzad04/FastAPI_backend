# handlers/task_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jwt_authentication.project.schemas.task_schema import tasksIn
from models.subtasks import Subtask
from schemas.subtasks_schema import SubtaskIn,SubtaskOut
from models.task import Task
from models.project import Project
from models.user import User

def create_subtask(db: Session, task_id: int, user: User, s:SubtaskIn):


    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to == user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you are not assigned to it"
        )

    # Create subtask
    subtask = Subtask(
        title=s.title,
        description=s.description,
        status=s.status,
        task_id=task_id
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask

def get_task_subtask(db: Session, task_id: int, user:User):

    if user.role_name=="admin":

        subtasks = db.query(Task).filter(Task.task_id == task_id).all()
    else:
        subtasks = db.query(Task).filter(Task.task_id == task_id, Task.assigned_to == user.id).all()

    if not  subtasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subtasks found"
        )

    return subtasks





def update_subtask( subtask_id: int,s: SubtaskIn,db: Session, user: User):
    # Find subtask, ensure it's under a task assigned to the user
    subtask = db.query(Subtask).join(Task).filter(
        Subtask.id == subtask_id,
        # Task.id == s.task_id,
        Task.assigned_to == user.id
    ).first()
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found or you are not authorized to update it"
        )

    
    subtask.status = s.status
    subtask.title = s.title
    subtask.description = s.description

    db.commit()
    db.refresh(subtask)
    return subtask

def delete_subtask( subtask_id: int,db: Session, user: User):

    subtask = db.query(Subtask).join(Task).filter(
        Subtask.id == subtask_id,
        Task.assigned_to == user.id,
       
    ).first()

    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found or unauthorized"
        )

    db.delete(subtask)
    db.commit()

    return {"msg": f"Subtask {subtask_id} deleted"}

# handlers/task_handler.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from schemas.task_schema import tasksIn
from models.subtasks import Subtask
from schemas.subtasks_schema import SubtaskIn,SubtaskOut
from models.task import Task
from models.project import Project
from models.user import User

def create_subtask(db: Session, task_id: int, user: User, s:SubtaskIn):


    task = db.query(Task).filter(
        Task.id == task_id,
        
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

def get_task_subtask(db: Session, task_id: int, user:User, page: int, no_records: int,search:str):
 # Start building the query (don't use .all() yet!)
    query = db.query(Subtask).join(Task).join(Project).filter(Subtask.task_id == task_id, Task.assigned_to == user.id, Task.project_id == Project.id, Project.org_id == user.org_id)

    # If user is not admin, restrict to assigned subtasks
    if user.role_name == "user":
        query = query.filter(Subtask.assigned_to == user.id)

    # Apply search filter if provided
    if search:
        query = query.filter(
            Subtask.title.ilike(f"%{search}%")  # Search in title
            # Note: no need to re-check task_id — already filtered above
        )

    # Now get total count and apply pagination
    total = query.count()  # Total matching subtasks
    start = (page - 1) * no_records

    if start >= total:
        raise HTTPException(status_code=404, detail="Page out of range")






def update_subtask( subtask_id: int,s: SubtaskIn,db: Session, user: User):
    # Find subtask, ensure it's under a task assigned to the user
    subtask = db.query(Subtask).join(Task).join(Project).filter(
        Subtask.id == subtask_id,
        # Task.id == s.task_id,
        Task.assigned_to == user.id,
        Project.org_id == user.org_id
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

    subtask = db.query(Subtask).join(Task).join(Project).filter(
        Subtask.id == subtask_id,
        Task.assigned_to == user.id,
        Project.org_id == user.org_id
    ).first()

    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found or unauthorized"
        )

    db.delete(subtask)
    db.commit()

    return {"msg": f"Subtask {subtask_id} deleted"}

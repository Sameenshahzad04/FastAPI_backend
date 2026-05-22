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

def get_task_subtask(db: Session, task_id: int, user:User, page: int, no_records: int):

    if user.role_name=="admin":

        subtasks = db.query(Subtask).filter(Subtask.task_id == task_id).all()
    else:
        subtasks = db.query(Subtask).filter(Subtask.task_id == task_id, Subtask.assigned_to == user.id).all()

    if not  subtasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subtasks found"
        )
    
    total = len(subtasks)
    start = (page - 1) * no_records

    if start >= total:
            raise HTTPException(status_code=404, detail="Page out of range")
    end = start + no_records
    # Slice the data
    if total>=no_records:
       
        paginated_data = subtasks[start:end]
    else:
         paginated_data = subtasks
    
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

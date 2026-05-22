from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.user import User
from jwt import get_current_user, role_required
from handlers.subtask_handler import create_subtask,update_subtask,delete_subtask,get_task_subtask

from typing import List

from schemas.subtasks_schema import SubtaskIn, SubtaskOut


subtask_routes = APIRouter()

# def createSubtask(db: Session, task_id: int, user: User, s: SubtaskIn):
   
#    return create_subtask(db, task_id, user, s)

# POST /tasks/{task_id}/subtasks
@subtask_routes.post('/tasks/{task_id}/subtasks', response_model=SubtaskOut)
def createSubtask( task_id: int, s: SubtaskIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    
    return create_subtask(db, task_id, user, s)


# PUT /subtasks/{subtask_id}
@subtask_routes.put('/subtasks/{subtask_id}', response_model=SubtaskOut)
def updateSubtask(   subtask_id: int,s: SubtaskIn, db: Session = Depends(get_db), user: User = Depends(get_current_user) ):
    
    return update_subtask(subtask_id,s, db, user)


@subtask_routes.delete('/subtasks/{subtask_id}', response_model=SubtaskOut)
def deleteSubtask(subtask_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user) ):
    
    return delete_subtask(db, subtask_id, user)

@subtask_routes.get('/substask/{task_id}/subtasks', response_model=List[SubtaskOut])
def getTaskSubtask(db: Session, task_id: int, user:User):


    return  get_task_subtask(db, task_id, user)
from fastapi import APIRouter, Depends, HTTPException,status ,Query
from sqlalchemy.orm import Session
from database import get_tenant_db
from models.task import Task
from models.user import User
from jwt import get_current_user, role_required,get_tenant_db_with_user
from handlers.subtask_handler import create_subtask,update_subtask,delete_subtask,get_task_subtask

from typing import List

from schemas.subtasks_schema import SubtaskIn, SubtaskOut
from schemas.page import Page


subtask_routes = APIRouter()

# def createSubtask(db: Session, task_id: int, user: User, s: SubtaskIn):
   
#    return create_subtask(db, task_id, user, s)

# POST /tasks/{task_id}/subtasks
@subtask_routes.post('/tasks/{task_id}/subtasks', response_model=SubtaskOut)
def createSubtask( task_id: int, s: SubtaskIn, db: Session = Depends(get_tenant_db_with_user), user: User = Depends(get_current_user)
):
    
    return create_subtask(db, task_id, user, s)


# PUT /subtasks/{subtask_id}
@subtask_routes.put('/subtasks/{subtask_id}', response_model=SubtaskOut)
def updateSubtask(   subtask_id: int,s: SubtaskIn, db: Session = Depends(get_tenant_db_with_user), user: User = Depends(get_current_user) ):
    
    return update_subtask(subtask_id,s, db, user)


@subtask_routes.delete('/subtasks/{subtask_id}', response_model=SubtaskOut)
def deleteSubtask(subtask_id: int, db: Session = Depends(get_tenant_db_with_user), user: User = Depends(get_current_user) ):
    
    return delete_subtask(db, subtask_id, user)

@subtask_routes.get('/substask/{task_id}', response_model=Page[SubtaskOut])
def getTaskSubtask(task_id: int,db: Session = Depends(get_tenant_db_with_user), user:User = Depends(get_current_user),
                     search: str = Query(None, description="Search by subtask title or task id or subtask id"),
                    page: int = Query(1, ge=1,description="page number"),
                  no_records: int = Query(5, description="number of records per page")):


    return  get_task_subtask(db, task_id, user, page, no_records, search)
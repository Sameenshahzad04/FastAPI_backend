from fastapi import APIRouter, Depends, HTTPException,status,Query
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.project import Project
from models.user import User
from jwt import get_current_user, role_required
from schemas.task_schema import TaskOut,tasksIn
from schemas.page import Page
from typing import List
from handlers.task_handler import create_task,get_project_tasks,update_task,delete_task,assign_task_to_user



#admin create task,delete task,assign task
#user can see tasks,update task and can create sub tasks

# POST /projects/{id}/tasks
# GET /projects/{id}/tasks
# PUT /tasks/{task_id}
# DELETE /tasks/{task_id
# Tasks belong to a project
# Tasks have status (pending, in_progress, completed

task_routes=APIRouter()

@task_routes.post('/projects/{P_id}/tasks',response_model=TaskOut)
def createTask(P_id,t:tasksIn,u: User = Depends(role_required( "org_admin")),db:Session=Depends(get_db)):
    
  
    return create_task(db,t.title,t.des,t.status,P_id,u)

 #get all task of one project
@task_routes.get('/projects/{p_id}/tasks',response_model=Page[TaskOut])
def show_task(p_id:int , u: User = Depends(get_current_user),db:Session=Depends(get_db),
              search: str = Query(None, description="Search by task title or project id, or assigned user id"),
                  page: int = Query(1, ge=1,description="page number"),
                  no_records: int = Query(5, description="number of records per page")  
                    ):


    return get_project_tasks(db,p_id,u,page,no_records,search)


# PUT /tasks/{task_id}
@task_routes.put('/tasks/{task_id}',response_model=TaskOut)
def updateTask(t_id:int ,t:tasksIn,db:Session=Depends(get_db), u: User = Depends(get_current_user)):

    
    return update_task(db,t_id,u,t)

   # del /tasks/{task_id}
@task_routes.delete('/tasks/{task_id}')
def del_task(t_id:int ,db:Session=Depends(get_db),u: User = Depends(role_required( "org_admin"))):

    return delete_task(db, t_id,u)


    
@task_routes.post("/assign/{task_id}/user/{user_id}", response_model=TaskOut)
def assign_task(task_id: int, user_id: int, db: Session = Depends(get_db), assigner: User = Depends((role_required( "org_admin")))):
    
    task = assign_task_to_user(db, task_id, user_id,assigner)
    return task
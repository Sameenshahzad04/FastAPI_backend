from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.project import Project
from models.user import User
from security import get_current_user
from schemas.task_schema import tasks,tasksIn
from typing import List
from handlers.task_handler import create_task,get_project_tasks,update_task,delete_task


# POST /projects/{id}/tasks
# GET /projects/{id}/tasks
# PUT /tasks/{task_id}
# DELETE /tasks/{task_id
# Tasks belong to a project
# Tasks have status (pending, in_progress, completed

task_routes=APIRouter()

@task_routes.post('/projects/{P_id}/tasks',response_model=tasks)
def createTask(P_id,t:tasksIn,u: User = Depends(get_current_user),db:Session=Depends(get_db)):
    
  
    return create_task(db,t.title,t.des,t.status,P_id,u.id)

 #get all task of one project
@task_routes.get('/projects/{p_id}/tasks',response_model=List[tasks])
def show_task(p_id:int , u: User = Depends(get_current_user),db:Session=Depends(get_db)):


    return get_project_tasks(db,p_id,u.id)


# PUT /tasks/{task_id}
@task_routes.put('/tasks/{task_id}',response_model=tasks)
def updateTask(t_id:int ,t:tasksIn,db:Session=Depends(get_db), u: User = Depends(get_current_user)):

    
    return update_task(db,t_id,u.id,t.title,t.des,t.status)

   # del /tasks/{task_id}
@task_routes.delete('/tasks/{task_id}')
def del_task(t_id:int ,db:Session=Depends(get_db),u: User = Depends(get_current_user)):

    
    

    return delete_task(db, t_id, u.id)


    

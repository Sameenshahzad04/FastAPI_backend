from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.project import Project
from schemas.task_schema import tasks,tasksIn
from typing import List


# POST /projects/{id}/tasks
# GET /projects/{id}/tasks
# PUT /tasks/{task_id}
# DELETE /tasks/{task_id
# Tasks belong to a project
# Tasks have status (pending, in_progress, completed

rou=APIRouter()

@rou.post('/projects/{P_id}/tasks',response_model=tasks)
def create_task(P_id,t:tasksIn,db:Session=Depends(get_db)):
    proj = db.query(Project).filter(Project.id == P_id).first()
    if  not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="project id is not present in db")
    my_task=Task(
        
        title=t.title,
        des=t.des,
        status=t.status,
        project_id=P_id


    )
    db.add(my_task)
    db.commit()
    db.refresh(my_task)
    return my_task

 #get all task of one project
@rou.get('/projects/{p_id}/tasks',response_model=List[tasks])
def show_task(p_id:int ,db:Session=Depends(get_db)):

    my_task=db.query(Task).filter(Task.project_id==p_id).all()
    if not my_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Project id is not found ")
    return my_task


# PUT /tasks/{task_id}
@rou.put('/tasks/{task_id}',response_model=tasks)
def update_task(t_id:int ,t:tasks,db:Session=Depends(get_db)):

    my_task=db.query(Task).filter(Task.id==t_id).first()
    if not my_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Project id is not found ")
    my_task.title=t.title
    my_task.des=t.des
    my_task.status=t.status
    my_task.project_id=t.project_id

    db.commit()
    db.refresh(my_task)

    return my_task

   # del /tasks/{task_id}
@rou.delete('/tasks/{task_id}')
def del_task(t_id:int ,db:Session=Depends(get_db)):

    my_task=db.query(Task).filter(Task.id==t_id).first()
    if not my_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="task id is not found ")
    else:
        db.delete(my_task)
        db.commit()
    

    return {"msg":f"task {t_id} is deleted"}
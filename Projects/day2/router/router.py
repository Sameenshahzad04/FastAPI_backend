

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field
from typing import List



router=APIRouter()


tasks:List[dict] = []
    




class TaskCreate(BaseModel):
    id:int
    task_name:str=Field(...,min_length=3)
    status:str
    owner:str
class TaskResponse(BaseModel):
    id:int
    task_name:str=Field(...,min_length=3)
    status:str
    

#



#return list of tasks
@router.get("/tasks",response_model=List[TaskCreate])
def li_task():
    return tasks

#get single task
@router.get("/tasks/{task_id}")
def Single_t(task_id:int):
    for t in tasks:
        if t["id"]==task_id:
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return {"message": "Task deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
#Add a task



@router.post("/tasks", response_model=TaskResponse)
def add_task(task: TaskCreate):

    new_task = {
        "id": task.id,
        "task_name": task.task_name,
        "status": task.status,
        "owner":task.owner
    }

    tasks.append(new_task)
    return new_task
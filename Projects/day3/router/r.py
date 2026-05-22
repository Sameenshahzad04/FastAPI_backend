
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from model.model import Task
from schema.schemas import Taskcr, TaskRes

rou = APIRouter()


#create task
@rou.post("/tasks", response_model=TaskRes)
async def create_task(t: Taskcr, db: Session = Depends(get_db)):
    new_task = Task(
        task_name=t.task_name,
        status=t.status,
        owner=t.owner
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


#get all task 

@rou.get("/", response_model=list[TaskRes])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


# UPDATE TASK

@rou.put("/tasks/{task_id}", response_model=TaskRes)
def update_task(task_id: int, updated_task: Taskcr, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.task_name = updated_task.task_name
    task.status = updated_task.status
    task.owner = updated_task.owner

    db.commit()
    db.refresh(task)

    return task


# DELETE TASK

@rou.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In-memory storage
tasks: List[dict] = []

class Task(BaseModel):
    id: int
    task_name: str 
    status: str

# Welcome message
@app.get("/")
def wel_msg():
    return {"message": "Welcome to Mini Project"}

# Return all tasks
@app.get("/tasks", response_model=List[Task])
def li_task():
    return tasks

# Get single task
@app.get("/tasks/{task_id}", response_model=Task)
def single_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return {"message": "Task id not found"}

# Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(index)
            return {"message": "Task deleted"}
    return {"message": "Task id not found"}

# Add a task

@app.post("/tasks", response_model=Task)

@app.post("/tasks", response_model=Task)
def add_task(task: Task):
    # Check if task ID already exists
    for t in tasks:
        if t["id"] == task.id:
            return {"msg":"not found id"}
    # Append new task to the global list
    tasks.append(task.dict())
    return task
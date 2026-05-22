from fastapi import FastAPI
from database import engine, Base
from models.user import User
from models.project import Project
from models.task import Task
from models.role import Role
from models.subtasks import Subtask
from models.organization import Organization
from routers import user_routes,project_routes,task_routes




Base.metadata.create_all(bind=engine)
app=FastAPI()

app.include_router(user_routes.user_routes,prefix='/users',tags=['users'])
app.include_router(project_routes.project_routes,prefix='/project',tags=['project'])
app.include_router(task_routes.task_routes, prefix='/tasks', tags=['tasks'])

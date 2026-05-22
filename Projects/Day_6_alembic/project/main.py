from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from routers import user_routes,project_routes,task_routes
from database import Base,engine



Base.metadata.create_all(bind=engine)
app=FastAPI()

app.include_router(user_routes.user_routes,prefix='/users',tags=['users'])
app.include_router(project_routes.project_routes,prefix='/project',tags=['project'])
app.include_router(task_routes.task_routes, prefix='', tags=['routers'])

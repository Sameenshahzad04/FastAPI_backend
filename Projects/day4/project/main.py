from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from routers import user_routes,project_routes,task_routes
from database import Base,engine



Base.metadata.create_all(bind=engine)
app=FastAPI()

app.include_router(user_routes.r,prefix='/user',tags=['user'])
app.include_router(project_routes.ro,prefix='/project',tags=['project'])
app.include_router(task_routes.rou, prefix='', tags=['routers'])
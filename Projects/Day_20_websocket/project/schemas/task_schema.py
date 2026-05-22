from pydantic import BaseModel
from typing import Literal
from schemas.user_schema import Userout

TaskStatus = Literal["pending", "in_progress", "completed"]


 
        
class tasksIn(BaseModel):
     #d:int
     title :str
     des:str 
     status: TaskStatus = "pending"
   #   project_id :int
   #   class Config:
   #      from_attributes = True 
class TaskOut(BaseModel):
    id: int
    title: str
    des: str
    status: TaskStatus = "pending"
    project_id: int
    assigned_user: Userout | None=None
    assigned_to: int | None = None
    class Config:
        from_attributes = True
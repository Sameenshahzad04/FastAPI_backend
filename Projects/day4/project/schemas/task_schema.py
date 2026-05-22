from pydantic import BaseModel
from typing import Literal

TaskStatus = Literal["pending", "in_progress", "completed"]


 

class tasks(BaseModel):
     id:int
     title :str
     des:str 
     status: TaskStatus = "pending"
     project_id :int
     class Config:
        from_attributes = True 
        
class tasksIn(BaseModel):
     #d:int
     title :str
     des:str 
     status: TaskStatus = "pending"
   #   project_id :int
   #   class Config:
   #      from_attributes = True 
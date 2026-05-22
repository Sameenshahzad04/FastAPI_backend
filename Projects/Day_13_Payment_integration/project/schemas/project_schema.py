from pydantic import BaseModel, Field
from schemas.task_schema import TaskOut





class Projectin(BaseModel):
    # id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    org_id:int=None
    #owner_id:int
    #assigned_to:int|None
    

class Projectinfo(BaseModel):
    id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    owner_id:int
    org_id:int=None
    # assigned_to:int|None
    
    class Config:
        from_attributes = True  
class Projectfind(BaseModel):
    #id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    # owner_id:int
    
    # class Config:
    #     from_attributes = True  
class ProjectWithTasks(BaseModel):
    id: int
    name: str
    des: str
    tasks: list[TaskOut] = []

    class Config:
        from_attributes = True
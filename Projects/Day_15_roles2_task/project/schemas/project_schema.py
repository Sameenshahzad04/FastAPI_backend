from pydantic import BaseModel, Field






class Projectin(BaseModel):
    # id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    #owner_id:int
    #assigned_to:int|None
    

class Projectinfo(BaseModel):
    id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    owner_id:int
    assigned_to:int|None
    
    class Config:
        from_attributes = True  
class Projectfind(BaseModel):
    #id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    # owner_id:int
    
    # class Config:
    #     from_attributes = True  

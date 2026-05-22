from pydantic import BaseModel, Field




class Projectinfo(BaseModel):
    id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    owner_id:int
    
    class Config:
        from_attributes = True  
class Projectfind(BaseModel):
    #id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    owner_id:int
    
    # class Config:
    #     from_attributes = True  
class Projectget(BaseModel):
    #id :int
    # name:str=Field(...,min_length=3)
    # des :str=Field(...,min_length=3)   
    owner_id:int
    
    # class Config:
    #     from_attributes = True  
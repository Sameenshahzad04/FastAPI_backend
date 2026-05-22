from pydantic import BaseModel, Field






class organizationDetails(BaseModel):
    id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    owner_id:int=None
    #assigned_to:int|None
class organizationin(BaseModel):
    # id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3)   
    # owner_id:int
    #assigned_to:int|None
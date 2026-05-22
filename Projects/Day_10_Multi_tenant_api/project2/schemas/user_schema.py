
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional,Literal


#for admin
# User_roles = Literal["super_admin","org_admin"]


User_roles = Literal["user","org_admin"]

class UserRegister(BaseModel):
    #id :int
    username :str=Field(...,min_length=3)
    email:EmailStr
    password :str=Field(...,min_length=5)
    role_name:User_roles
    org_id:int|None=None

    

    stripe_payment_method_id: Literal[ "pm_card_visa"] = "pm_card_visa"
    pricing_plan: Literal["basic", "pro"] = "basic"

    class Config:
        from_attributes = True

class CreateUser(BaseModel):
    
    email:EmailStr
    password :str=Field(...,min_length=5)
    
 

class Userout(BaseModel):
    id :int
    username :str=Field(...,min_length=3)
    email:EmailStr
    org_id:int|None=None
    
    # it is use when you show/take data from db to (show)user but as db obj is sql ,and py is dict so it say use orm to show data 
    class Config:
        from_attributes = True 
        
class LoginResponse(BaseModel):
    message: str
    user: Userout

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message:str

class TokenData(BaseModel):
    username: Optional[str] = None  

class Userupdate(BaseModel):
    #id :int
    username :str=Field(...,min_length=3)
    email:EmailStr
    # password :str=Field(...,min_length=5)
    role_name:User_roles
    org_id:int|None=None

    stripe_payment_method_id: Literal[ "pm_card_visa"] = "pm_card_visa"
    pricing_plan: Literal["basic", "pro"] = "basic"

    class Config:
        from_attributes = True















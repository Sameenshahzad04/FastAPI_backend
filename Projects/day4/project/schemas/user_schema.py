

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    #id :int
    username :str=Field(...,min_length=3)
    email:EmailStr
    password :str=Field(...,min_length=5)
    


class UserLogin(BaseModel):
    
    email:EmailStr
    password :str=Field(...,min_length=5)
    
 

class Userout(BaseModel):
    id :int
    username :str=Field(...,min_length=3)
    email:EmailStr
    # it is use when you show/take data from db to (show)user but as db obj is sql ,and py is dict so it say use orm to show data 
    class Config:
        from_attributes = True 
        
class LoginResponse(BaseModel):
    message: str
    user: Userout

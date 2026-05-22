from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ChatMessage(BaseModel):
   
    type: str = "message"  
    sender_id: int
    sender_name: str
    content: str
    timestamp: Optional[str] = None

class JoinMessage(BaseModel):
   
    type: str = "joined"
    user_id: int
    username: str

class LeaveMessage(BaseModel):
 
    type: str = "left"
    user_id: int
    username: str
 

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

class UserRegister(BaseModel):
    #id :int
    username :str=Field(...,min_length=3)
    email:EmailStr
    # password :str=Field(...,min_length=5)
    
from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    type: str = "message"
    content: str
    to: Optional[int] = None

class MessageOut(BaseModel):
    type: str
    from_user_id: int
    from_username: str
    content: str
    timestamp: str
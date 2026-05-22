from pydantic import BaseModel
from typing import Literal
from schemas.user_schema import Userout  

SubtaskStatusLiteral = Literal["pending", "in_progress", "completed"]

class SubtaskIn(BaseModel):
    title: str
    description: str | None = None
    status: SubtaskStatusLiteral = "pending"
    # task_id: int
    

class SubtaskOut(BaseModel):
    # id: int
    title: str
    description: str | None
    status: SubtaskStatusLiteral
    task_id: int
    # Optionally include assigned_user if subtasks inherit assignment, but assuming user manages their own subtasks

    class Config:
        from_attributes = True
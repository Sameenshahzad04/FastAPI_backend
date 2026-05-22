from pydantic import BaseModel

class Taskcr(BaseModel):
    task_name: str
    status: str
    owner: str


class TaskRes(BaseModel):
    id: int
    task_name: str
    status: str
    owner: str

    class Config:
        from_attributes = True  



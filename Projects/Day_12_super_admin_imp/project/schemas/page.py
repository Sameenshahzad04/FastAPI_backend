from pydantic import BaseModel, EmailStr, Field
from typing import Optional,List,Generic,TypeVar
from schemas.user_schema import Userout

resources=TypeVar("resources")

class Page(BaseModel, Generic[resources]):
    page :int
    records: int
    total: int # Total number of records e.g user
    pages: int  # Total number of pages
    data: List[resources]
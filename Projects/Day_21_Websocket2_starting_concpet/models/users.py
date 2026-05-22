from database import Base,get_db
from sqlalchemy import Column,Integer,String

from sqlalchemy.orm import relationship


    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email= Column(String, nullable=False)
    
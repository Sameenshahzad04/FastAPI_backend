
from sqlalchemy import  Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base



#creating table structure or model
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    des= Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project",cascade="all, delete")
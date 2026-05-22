
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
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
   
    tasks = relationship("Task", back_populates="project",cascade="all, delete")
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    assigned_user = relationship("User", back_populates="assigned_projects", foreign_keys=[assigned_to])

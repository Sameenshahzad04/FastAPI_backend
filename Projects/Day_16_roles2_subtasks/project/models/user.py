from database import Base,get_db
from sqlalchemy import Column, ForeignKey,Integer,String

from sqlalchemy.orm import relationship


    #creating table structure or model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email= Column(String, nullable=False)
    password = Column(String, nullable=False)
    
    role_name = Column(String, ForeignKey("roles.role_name"))
    role = relationship("Role", back_populates="users")

 # Projects created by admin
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")

    # Projects assigned to user
    assigned_task= relationship("Task", back_populates="assigned_user", foreign_keys="Task.assigned_to")
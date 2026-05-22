
from sqlalchemy import  Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from base import Base
from models.subtasks import Subtask

#creating table structure or model
class Task(Base):
    __tablename__ = "task"
    # __table_args__ = ({"schema": "org1"},)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    des= Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    

    project_id = Column(Integer, ForeignKey("projects.id"))
    # org_id = Column(Integer, ForeignKey("organization.id"))
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship(
        "User",
        back_populates="assigned_tasks",foreign_keys=[assigned_to]
       
    )
    subtasks = relationship("Subtask", back_populates="parent_task", cascade="all, delete-orphan")

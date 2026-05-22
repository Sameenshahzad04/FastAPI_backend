
from sqlalchemy import  Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base



class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)

    parent_task = relationship("Task", back_populates="subtasks")
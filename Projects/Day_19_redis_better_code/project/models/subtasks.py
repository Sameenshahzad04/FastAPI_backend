
from sqlalchemy import  Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from base import Base



class Subtask(Base):
    __tablename__ = "subtasks"
    # __table_args__ = ({"schema": "org1"},)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    # task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    # org_id = Column(Integer, ForeignKey("organization.id"))
    parent_task = relationship("Task", back_populates="subtasks")
    task_id = Column(Integer, ForeignKey("task.id"))


from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from base import Base
from datetime import datetime, timezone
from models.project import Project
from models.organization import Organization
from models.task import Task
from models.roles import Role

class User(Base):
    __tablename__ = "users"
    # telling that this table will be in share schema
    # __table_args__ = ({"schema": "},)
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    role_name = Column(String, ForeignKey("roles.role_name"))
    # role = relationship("Role",foreign_keys=[role_name])
    
    

    # Payment fields
    stripe_payment_method_id = Column(String)
    pricing_plan = Column(String, default="basic")
    is_active = Column(Boolean, default=False)
    first_login_done = Column(Boolean, default=False)
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
   

 # Projects created by admin
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    owned_organizations = relationship("Organization", back_populates="owner", foreign_keys="Organization.owner_id")
    # Projects assigned to user
    assigned_tasks= relationship("Task", back_populates="assigned_user", foreign_keys="Task.assigned_to")
    organization = relationship("Organization", back_populates="users",foreign_keys=[org_id])
    # role = relationship("Role")
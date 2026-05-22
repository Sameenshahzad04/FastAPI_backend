
from sqlalchemy import  Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base



#creating table structure or model
class Organization(Base):
    __tablename__ = "organization"

    id= Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    des= Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
   
    owner = relationship("User", back_populates="owned_organizations", foreign_keys=[owner_id])
    # assigned_user = relationship("User", back_populates="assigned_organizations", foreign_keys=[assigned_to])

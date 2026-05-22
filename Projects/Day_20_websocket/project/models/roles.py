from base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"
    # __table_args__ = ({"schema": "public"},)
    # role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, primary_key=True)
    #permission = Column(String, nullable=False)
    # users = relationship("User", back_populates="role", foreign_keys=[role_name])
    
    

   
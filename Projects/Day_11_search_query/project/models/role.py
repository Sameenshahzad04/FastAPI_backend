from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"

    # role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, primary_key=True)
    #permission = Column(String, nullable=False)
    users = relationship("User", back_populates="role")
    
    # users = relationship("User", back_populates="role")

   
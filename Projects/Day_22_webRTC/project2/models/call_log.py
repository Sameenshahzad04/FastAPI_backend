from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime, timezone
import enum

class CallType(enum.Enum):
    audio = "audio"
    video = "video"

class CallStatus(enum.Enum):
    initiated = "initiated"
    answered = "answered"
    missed = "missed"
    rejected = "rejected"
    ended = "ended"

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    caller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    call_type = Column(String, default="audio")  # audio or video
    status = Column(String, default="initiated")  # initiated, answered, missed, etc.
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Relationships
    caller = relationship("User", foreign_keys=[caller_id], backref="made_calls")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_calls")
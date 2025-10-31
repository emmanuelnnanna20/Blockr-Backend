from sqlalchemy import Column, String, DateTime, Date, Time, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.database import Base


class TimeBlockStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"


class TimeBlock(Base):
    __tablename__ = "time_blocks"
    
    time_block_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.task_id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(TimeBlockStatus), default=TimeBlockStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="time_blocks")
    task = relationship("Task", back_populates="time_blocks")
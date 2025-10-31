from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"
    
    task_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_list_id = Column(String(36), ForeignKey("task_lists.task_list_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task_list = relationship("TaskList", back_populates="tasks")
    time_blocks = relationship("TimeBlock", back_populates="task")
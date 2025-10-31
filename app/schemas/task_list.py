from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class TaskListBase(BaseModel):
    title: str
    duration_type: str
    start_date: date
    end_date: date


class TaskListCreate(TaskListBase):
    pass


class TaskListUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None


class TaskListResponse(TaskListBase):
    task_list_id: str
    user_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    
    class Config:
        from_attributes = True
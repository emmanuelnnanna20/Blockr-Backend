from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str


class TaskCreate(TaskBase):
    task_list_id: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskResponse(TaskBase):
    task_id: str
    task_list_id: str
    is_completed: bool
    completed_at: Optional[datetime] = None
    order_index: int
    created_at: datetime
    
    class Config:
        from_attributes = True
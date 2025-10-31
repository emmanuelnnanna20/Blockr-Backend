from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional


class TimeBlockBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    notes: Optional[str] = None


class TimeBlockCreate(TimeBlockBase):
    task_id: Optional[str] = None


class TimeBlockUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class TimeBlockResponse(TimeBlockBase):
    time_block_id: str
    user_id: str
    task_id: Optional[str] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    task_title: Optional[str] = None
    
    class Config:
        from_attributes = True
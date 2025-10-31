from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.time_block import TimeBlock
from app.models.task import Task
from app.schemas.time_block import TimeBlockCreate, TimeBlockUpdate, TimeBlockResponse

router = APIRouter()


@router.post("", response_model=dict)
def create_time_block(
    time_block_in: TimeBlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new time block"""
    # Verify task belongs to user if task_id is provided
    if time_block_in.task_id:
        task = db.query(Task).join(Task.task_list).filter(
            Task.task_id == time_block_in.task_id,
            Task.task_list.has(user_id=current_user.user_id)
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
    
    time_block = TimeBlock(
        user_id=current_user.user_id,
        task_id=time_block_in.task_id,
        date=time_block_in.date,
        start_time=time_block_in.start_time,
        end_time=time_block_in.end_time,
        notes=time_block_in.notes
    )
    
    db.add(time_block)
    db.commit()
    db.refresh(time_block)
    
    # Get task title if exists
    task_title = None
    if time_block.task_id:
        task = db.query(Task).filter(Task.task_id == time_block.task_id).first()
        task_title = task.title if task else None
    
    return {
        "message": "Time block created successfully",
        "time_block": {
            "time_block_id": time_block.time_block_id,
            "user_id": time_block.user_id,
            "task_id": time_block.task_id,
            "date": time_block.date,
            "start_time": str(time_block.start_time),
            "end_time": str(time_block.end_time),
            "status": time_block.status.value,
            "notes": time_block.notes,
            "completed_at": time_block.completed_at,
            "created_at": time_block.created_at,
            "task_title": task_title
        }
    }


@router.get("", response_model=dict)
def get_time_blocks(
    date_filter: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Get time blocks for current user, optionally filtered by date"""
    query = db.query(TimeBlock).filter(TimeBlock.user_id == current_user.user_id)
    
    if date_filter:
        query = query.filter(TimeBlock.date == date_filter)
    
    time_blocks = query.offset(skip).limit(limit).all()
    
    result = []
    for tb in time_blocks:
        task_title = None
        if tb.task_id:
            task = db.query(Task).filter(Task.task_id == tb.task_id).first()
            task_title = task.title if task else None
        
        result.append({
            "time_block_id": tb.time_block_id,
            "user_id": tb.user_id,
            "task_id": tb.task_id,
            "date": tb.date,
            "start_time": str(tb.start_time),
            "end_time": str(tb.end_time),
            "status": tb.status.value,
            "notes": tb.notes,
            "completed_at": tb.completed_at,
            "created_at": tb.created_at,
            "task_title": task_title
        })
    
    return {"time_blocks": result}


@router.get("/{time_block_id}", response_model=dict)
def get_time_block(
    time_block_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific time block"""
    time_block = db.query(TimeBlock).filter(
        TimeBlock.time_block_id == time_block_id,
        TimeBlock.user_id == current_user.user_id
    ).first()
    
    if not time_block:
        raise HTTPException(status_code=404, detail="Time block not found")
    
    task_title = None
    if time_block.task_id:
        task = db.query(Task).filter(Task.task_id == time_block.task_id).first()
        task_title = task.title if task else None
    
    return {
        "time_block": {
            "time_block_id": time_block.time_block_id,
            "user_id": time_block.user_id,
            "task_id": time_block.task_id,
            "date": time_block.date,
            "start_time": str(time_block.start_time),
            "end_time": str(time_block.end_time),
            "status": time_block.status.value,
            "notes": time_block.notes,
            "completed_at": time_block.completed_at,
            "created_at": time_block.created_at,
            "task_title": task_title
        }
    }


@router.patch("/{time_block_id}", response_model=dict)
def update_time_block(
    time_block_id: str,
    time_block_in: TimeBlockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a time block"""
    time_block = db.query(TimeBlock).filter(
        TimeBlock.time_block_id == time_block_id,
        TimeBlock.user_id == current_user.user_id
    ).first()
    
    if not time_block:
        raise HTTPException(status_code=404, detail="Time block not found")
    
    update_data = time_block_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(time_block, field, value)
    
    db.commit()
    db.refresh(time_block)
    
    return {"message": "Time block updated successfully"}


@router.delete("/{time_block_id}", response_model=dict)
def delete_time_block(
    time_block_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a time block"""
    time_block = db.query(TimeBlock).filter(
        TimeBlock.time_block_id == time_block_id,
        TimeBlock.user_id == current_user.user_id
    ).first()
    
    if not time_block:
        raise HTTPException(status_code=404, detail="Time block not found")
    
    db.delete(time_block)
    db.commit()
    
    return {"message": "Time block deleted successfully"}
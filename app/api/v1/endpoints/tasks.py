from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.task_list import TaskList
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("", response_model=dict)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task"""
    # Verify task list belongs to user
    task_list = db.query(TaskList).filter(
        TaskList.task_list_id == task_in.task_list_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")
    
    # Get next order index
    max_order = db.query(Task).filter(
        Task.task_list_id == task_in.task_list_id
    ).count()
    
    task = Task(
        task_list_id=task_in.task_list_id,
        title=task_in.title,
        order_index=max_order
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return {
        "message": "Task created successfully",
        "task": {
            "task_id": task.task_id,
            "task_list_id": task.task_list_id,
            "title": task.title,
            "is_completed": task.is_completed,
            "completed_at": task.completed_at,
            "order_index": task.order_index,
            "created_at": task.created_at
        }
    }


@router.get("/{task_id}", response_model=dict)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific task"""
    task = db.query(Task).join(TaskList).filter(
        Task.task_id == task_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task": {
            "task_id": task.task_id,
            "task_list_id": task.task_list_id,
            "title": task.title,
            "is_completed": task.is_completed,
            "completed_at": task.completed_at,
            "order_index": task.order_index,
            "created_at": task.created_at
        }
    }


@router.put("/{task_id}", response_model=dict)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a task"""
    task = db.query(Task).join(TaskList).filter(
        Task.task_id == task_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return {"message": "Task updated successfully"}


@router.patch("/{task_id}/toggle", response_model=dict)
def toggle_task_completion(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle task completion status"""
    task = db.query(Task).join(TaskList).filter(
        Task.task_id == task_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.is_completed = not task.is_completed
    task.completed_at = datetime.utcnow() if task.is_completed else None
    
    db.commit()
    db.refresh(task)
    
    return {
        "message": "Task status updated",
        "task": {
            "task_id": task.task_id,
            "is_completed": task.is_completed,
            "completed_at": task.completed_at
        }
    }


@router.delete("/{task_id}", response_model=dict)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a task"""
    task = db.query(Task).join(TaskList).filter(
        Task.task_id == task_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}
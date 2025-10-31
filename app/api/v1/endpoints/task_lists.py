from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.task_list import TaskList
from app.models.task import Task
from app.schemas.task_list import TaskListCreate, TaskListUpdate, TaskListResponse

router = APIRouter()


@router.post("", response_model=dict)
def create_task_list(
    task_list_in: TaskListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task list"""
    task_list = TaskList(
        user_id=current_user.user_id,
        title=task_list_in.title,
        duration_type=task_list_in.duration_type,
        start_date=task_list_in.start_date,
        end_date=task_list_in.end_date
    )
    
    db.add(task_list)
    db.commit()
    db.refresh(task_list)
    
    return {
        "message": "Task list created successfully",
        "task_list": {
            "task_list_id": task_list.task_list_id,
            "user_id": task_list.user_id,
            "title": task_list.title,
            "duration_type": task_list.duration_type,
            "start_date": task_list.start_date,
            "end_date": task_list.end_date,
            "status": task_list.status.value,
            "created_at": task_list.created_at,
            "completed_at": task_list.completed_at,
            "total_tasks": 0,
            "completed_tasks": 0
        }
    }


@router.get("", response_model=dict)
def get_task_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all task lists for current user"""
    task_lists = db.query(TaskList).filter(
        TaskList.user_id == current_user.user_id
    ).offset(skip).limit(limit).all()
    
    # Add task counts
    result = []
    for task_list in task_lists:
        total_tasks = db.query(Task).filter(Task.task_list_id == task_list.task_list_id).count()
        completed_tasks = db.query(Task).filter(
            Task.task_list_id == task_list.task_list_id,
            Task.is_completed == True
        ).count()
        
        result.append({
            "task_list_id": task_list.task_list_id,
            "user_id": task_list.user_id,
            "title": task_list.title,
            "duration_type": task_list.duration_type,
            "start_date": task_list.start_date,
            "end_date": task_list.end_date,
            "status": task_list.status.value,
            "created_at": task_list.created_at,
            "completed_at": task_list.completed_at,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks
        })
    
    return {"task_lists": result}


@router.get("/{task_list_id}", response_model=dict)
def get_task_list(
    task_list_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific task list"""
    task_list = db.query(TaskList).filter(
        TaskList.task_list_id == task_list_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")
    
    total_tasks = db.query(Task).filter(Task.task_list_id == task_list.task_list_id).count()
    completed_tasks = db.query(Task).filter(
        Task.task_list_id == task_list.task_list_id,
        Task.is_completed == True
    ).count()
    
    return {
        "task_list": {
            "task_list_id": task_list.task_list_id,
            "user_id": task_list.user_id,
            "title": task_list.title,
            "duration_type": task_list.duration_type,
            "start_date": task_list.start_date,
            "end_date": task_list.end_date,
            "status": task_list.status.value,
            "created_at": task_list.created_at,
            "completed_at": task_list.completed_at,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks
        }
    }


@router.put("/{task_list_id}", response_model=dict)
def update_task_list(
    task_list_id: str,
    task_list_in: TaskListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a task list"""
    task_list = db.query(TaskList).filter(
        TaskList.task_list_id == task_list_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")
    
    update_data = task_list_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task_list, field, value)
    
    db.commit()
    db.refresh(task_list)
    
    return {"message": "Task list updated successfully"}


@router.delete("/{task_list_id}", response_model=dict)
def delete_task_list(
    task_list_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a task list"""
    task_list = db.query(TaskList).filter(
        TaskList.task_list_id == task_list_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")
    
    db.delete(task_list)
    db.commit()
    
    return {"message": "Task list deleted successfully"}


@router.get("/{task_list_id}/tasks", response_model=dict)
def get_tasks_for_list(
    task_list_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks for a specific task list"""
    # Verify task list belongs to user
    task_list = db.query(TaskList).filter(
        TaskList.task_list_id == task_list_id,
        TaskList.user_id == current_user.user_id
    ).first()
    
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")
    
    tasks = db.query(Task).filter(Task.task_list_id == task_list_id).order_by(Task.order_index).all()
    
    return {
        "tasks": [
            {
                "task_id": task.task_id,
                "task_list_id": task.task_list_id,
                "title": task.title,
                "is_completed": task.is_completed,
                "completed_at": task.completed_at,
                "order_index": task.order_index,
                "created_at": task.created_at
            }
            for task in tasks
        ]
    }
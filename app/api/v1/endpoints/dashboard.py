from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.task_list import TaskList, TaskListStatus
from app.models.task import Task
from app.models.time_block import TimeBlock, TimeBlockStatus

router = APIRouter()


@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics for current user"""
    
    # Task Lists Stats
    total_task_lists = db.query(TaskList).filter(
        TaskList.user_id == current_user.user_id
    ).count()
    
    completed_task_lists = db.query(TaskList).filter(
        TaskList.user_id == current_user.user_id,
        TaskList.status == TaskListStatus.COMPLETED
    ).count()
    
    # Tasks Stats
    total_tasks = db.query(Task).join(TaskList).filter(
        TaskList.user_id == current_user.user_id
    ).count()
    
    completed_tasks = db.query(Task).join(TaskList).filter(
        TaskList.user_id == current_user.user_id,
        Task.is_completed == True
    ).count()
    
    # Today's Time Blocks
    today = date.today()
    today_time_blocks = db.query(TimeBlock).filter(
        TimeBlock.user_id == current_user.user_id,
        TimeBlock.date == today
    ).count()
    
    completed_time_blocks = db.query(TimeBlock).filter(
        TimeBlock.user_id == current_user.user_id,
        TimeBlock.date == today,
        TimeBlock.status == TimeBlockStatus.COMPLETED
    ).count()
    
    missed_time_blocks = db.query(TimeBlock).filter(
        TimeBlock.user_id == current_user.user_id,
        TimeBlock.date == today,
        TimeBlock.status == TimeBlockStatus.MISSED
    ).count()
    
    # Calculate overall completion percentage
    overall_completion = 0.0
    if total_tasks > 0:
        overall_completion = (completed_tasks / total_tasks) * 100
    
    return {
        "total_task_lists": total_task_lists,
        "completed_task_lists": completed_task_lists,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "today_time_blocks": today_time_blocks,
        "completed_time_blocks": completed_time_blocks,
        "missed_time_blocks": missed_time_blocks,
        "overall_completion": round(overall_completion, 2)
    }
# Import Base first
from app.db.database import Base

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.task_list import TaskList
from app.models.task import Task
from app.models.time_block import TimeBlock
from app.models.subscription import Subscription

# This ensures all models are registered with Base.metadata
__all__ = ["Base", "User", "TaskList", "Task", "TimeBlock", "Subscription"]
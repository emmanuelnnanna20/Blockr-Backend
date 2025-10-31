from fastapi import APIRouter
from app.api.v1.endpoints import auth, task_lists, tasks, time_blocks, dashboard, subscription

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(task_lists.router, prefix="/task-lists", tags=["Task Lists"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(time_blocks.router, prefix="/time-blocks", tags=["Time Blocks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["Subscription"])
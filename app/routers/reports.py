from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas import TaskRead
from app.services.tasks import TaskService
from app.dependencies import get_task_service, get_current_user


router = APIRouter(prefix="/reports")


@router.get(
    "/projects/{project_id}/status-count", response_model=list[dict[str, Any]]
)
def get_status_report(project_id: int, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    try:
        return task_service.get_status_report(project_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/overdue", response_model=list[TaskRead])
def overdue_tasks(project_id: int, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    try:
        return task_service.get_overdue_tasks_in_project(project_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

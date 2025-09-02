from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.models.enums import Priority, Role, TaskStatus
from app.schemas import TaskRead, TaskCreate, TaskStatusUpdate
from app.dependencies import get_current_user, get_task_service, require_role
from app.services.tasks import TaskService

router = APIRouter()


@router.post("/projects/{project_id}/tasks", response_model=TaskRead)
def create_task(
    project_id: int,
    task_in: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.create_task(project_id, task_in, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def get_tasks_in_project(
    project_id: int,
    status: TaskStatus | None = None,
    assignee_id: int | None = None,
    priority: Priority | None = None,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.get_tasks_in_project(
            project_id, current_user, status, assignee_id, priority
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    try:
        return task_service.get_by_id(task_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/tasks/{task_id}/assignee", response_model=TaskRead)
def update_assignee(
    task_id: int,
    assignee_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.update_assignee(task_id, assignee_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    task_in: TaskStatusUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.update_task_status(task_id, task_in, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(require_role(Role.ADMIN))):
    try:
        task_service.delete_task(task_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

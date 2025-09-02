from fastapi import APIRouter, Depends, HTTPException
from app.models.enums import Role
from app.models.user import User
from app.schemas import ProjectRead, ProjectBase
from app.dependencies import get_current_user, get_project_service, require_role
from app.schemas.user import UserRead
from app.services.projects import ProjectService

router = APIRouter(prefix="/projects")


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(
    project_in: ProjectBase,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(require_role(Role.ADMIN, Role.MANAGER)),
):
    try:
        return project_service.create_project(project_in, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_service.get_all(current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}", response_model=ProjectRead)
def read_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_service.get_by_id(project_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/members", response_model=list[UserRead])
def list_members(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_service.list_members(project_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{project_id}/members", response_model=UserRead, status_code=201)
def add_member(
    project_id: int,
    user_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(require_role(Role.ADMIN, Role.MANAGER)),
):
    try:
        return project_service.add_member(project_id, user_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_member(
    project_id: int,
    user_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(require_role(Role.ADMIN, Role.MANAGER)),
):
    try:
        project_service.remove_member(project_id, user_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

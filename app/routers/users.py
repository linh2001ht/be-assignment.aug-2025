from fastapi import APIRouter, Depends, HTTPException
from app.models.enums import Role
from app.models.user import User
from app.schemas import UserRead
from app.dependencies import get_current_user_no_org, require_role, get_user_service
from app.services.users import UserService

router = APIRouter(prefix="/users")

@router.get("/", response_model=list[UserRead])
def list_users(user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserRead)
def read_user_me(current_user: User = Depends(get_current_user_no_org)):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{user_id}/role")
def update_role(user_id: int, role: Role, current_user: User =Depends(require_role(Role.ADMIN)), user_service: UserService =Depends(get_user_service)):
    try:
        return user_service.change_user_role(user_id, role, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas import CommentRead, CommentBase
from app.dependencies import get_current_user, get_comment_service
from app.services.comments import CommentService

router = APIRouter(prefix="/tasks/{task_id}/comments")

@router.post("/", response_model=CommentRead)
def add_comment(task_id: int, comment_in: CommentBase, current_user: User = Depends(get_current_user), comment_service: CommentService = Depends(get_comment_service)):
    try:
        return comment_service.add_comment(task_id, comment_in, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[CommentRead])
def list_comments(task_id: int, current_user: User = Depends(get_current_user), comment_service: CommentService = Depends(get_comment_service)):
    try:
        return comment_service.list_comments(task_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

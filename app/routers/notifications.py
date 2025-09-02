from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas import NotificationRead
from app.dependencies import get_current_user, get_notification_service
from app.services.notifications import NotificationService

router = APIRouter(prefix="/notifications")

@router.get("/", response_model=list[NotificationRead])
def get_unread(current_user: User = Depends(get_current_user), notification_service : NotificationService=Depends(get_notification_service)):
    try:
        return notification_service.get_unread_notifications(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

@router.patch("/{notif_id}/read")
def mark_read(notif_id: int, current_user: User = Depends(get_current_user), notification_service: NotificationService = Depends(get_notification_service)):
    try:
        if notification_service.mark_as_read(current_user.id, notif_id):
            return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

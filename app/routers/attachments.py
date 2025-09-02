from fastapi import APIRouter, Depends, UploadFile, HTTPException
from app.models.user import User
from app.schemas import AttachmentRead
from app.dependencies import get_current_user, get_attachment_service
from app.services.attachments import AttachmentService

router = APIRouter()


@router.post("/tasks/{task_id}/attachments", response_model=AttachmentRead)
def upload(
    task_id: int,
    file: UploadFile,
    attachments_service: AttachmentService = Depends(get_attachment_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return attachments_service.upload_attachment(task_id, file, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}/attachments", response_model=list[AttachmentRead])
def get_attachments(
    task_id: int,
    attachments_service: AttachmentService = Depends(get_attachment_service),
    current_user: User = Depends(get_current_user),
):  
    try:
        return attachments_service.get_attachments(task_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{attachment_id}", response_model=AttachmentRead)
def get_attachment(
    attachment_id: int,
    attachments_service: AttachmentService = Depends(get_attachment_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return attachments_service.get_by_id(attachment_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{attachment_id}", status_code=204)
def delete_attachment(
    attachment_id: int,
    attachments_service: AttachmentService = Depends(get_attachment_service),
    current_user: User = Depends(get_current_user),
):
    try:
        attachments_service.delete_attachment(attachment_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
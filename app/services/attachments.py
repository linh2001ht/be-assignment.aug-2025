import os
import uuid
from fastapi import UploadFile
from app.config import settings
from app.models import Attachment, User
from app.models.enums import Role
from app.repositories.attachments import AttachmentRepository
from app.services.tasks import TaskService


class AttachmentService:
    def __init__(
        self, attachment_repo: AttachmentRepository, task_service: TaskService
    ):
        self.attachment_repo = attachment_repo
        self.task_service = task_service

    def get_by_id(self, attachment_id: int, current_user: User) -> Attachment:
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise ValueError("Attachment not found.")
        task = self.task_service.get_by_id(attachment.task_id, current_user)
        if current_user.role != Role.ADMIN and attachment.user_id != current_user.id:
            raise ValueError("Not authorized to access this attachment.")
        return attachment

    def get_attachments(self, task_id: int, current_user: User) -> list[Attachment]:
        self.task_service.get_by_id(task_id, current_user)
        return self.attachment_repo.get_by_task(task_id)

    def upload_attachment(
        self, task_id: int, file: UploadFile, current_user: User
    ) -> Attachment:
        # Business Rule: User must have access to the task's project
        task = self.task_service.get_by_id(task_id, current_user)

        if len(task.attachments) >= settings.max_files_per_task:
            raise ValueError("Max 3 attachments per task.")

        contents = file.file.read()
        file_size = len(contents)
        if file_size > settings.max_file_size:
            raise ValueError("File too large")
        file.file.seek(0)

        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        unique_id = uuid.uuid4()
        filename = f"{unique_id}{ext}"
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, "wb") as f:
            f.write(contents)

        attachment_data = {
            "size": file_size,
            "path": filepath,
            "filename": filename,
            "task_id": task_id,
            "user_id": current_user.id,
        }
        attachment = self.attachment_repo.create(**attachment_data)

        return attachment

    def delete_attachment(self, attachment_id: int, current_user: User) -> None:
        attachment = self.get_by_id(attachment_id, current_user)
        if current_user.role != Role.ADMIN and attachment.user_id != current_user.id:
            raise ValueError("You do not have permission to delete this attachment.")
        try:
            os.remove(attachment.path)
        except OSError:
            pass
        self.attachment_repo.delete(attachment)
        

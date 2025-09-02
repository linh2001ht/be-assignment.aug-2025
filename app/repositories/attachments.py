from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import Attachment

class AttachmentRepository(BaseRepository[Attachment]):
    def __init__(self, db: Session):
        super().__init__(db, Attachment)

    def get_by_task(self, task_id: int) -> list[Attachment]:
        return self.db.query(self.model).filter(self.model.task_id == task_id).all()
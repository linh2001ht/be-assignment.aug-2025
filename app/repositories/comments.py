# app/repositories/comments.py

from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import Comment

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(db, Comment)

    def get_by_task(self, task_id: int) -> list[Comment]:
        return self.db.query(self.model).filter(self.model.task_id == task_id).all()
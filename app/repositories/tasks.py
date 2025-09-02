from typing import Any
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import Task, TaskStatus, Priority
from sqlalchemy import func
from datetime import date


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(db, Task)

    def get_filtered_tasks(
        self,
        project_id: int,
        status: TaskStatus | None = None,
        assignee_id: int | None = None,
        priority: Priority | None = None,
    ) -> list[Task]:
        query = self.db.query(self.model).filter(
            self.model.project_id == project_id
        )

        if status:
            query = query.filter(self.model.status == status)
        if assignee_id:
            query = query.filter(self.model.assignee_id == assignee_id)
        if priority:
            query = query.filter(self.model.priority == priority)

        return query.all()

    def get_count_by_status(self, project_id: int) -> list[dict[str, Any]]:
        results = (
            self.db.query(self.model.status, func.count(self.model.id).label("task_count"))
            .filter(self.model.project_id == project_id)
            .group_by(self.model.status)
            .all()
        )

        return [{"status": r.status.value, "count": r.task_count} for r in results]

    def get_overdue(self, project_id: int) -> list[Task]:
        return (
            self.db.query(self.model)
            .filter(
                self.model.project_id == project_id,
                self.model.due_date < date.today(),
                self.model.status != TaskStatus.DONE,
            )
            .all()
        )

from datetime import date
from pydantic import BaseModel
from app.models import TaskStatus, Priority

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: Priority = Priority.LOW
    due_date: date

class TaskCreate(TaskBase):
    assignee_id: int | None = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskRead(TaskBase):
    id: int
    status: TaskStatus
    assignee_id: int | None = None
    project_id: int

    class Config:
        from_attributes = True

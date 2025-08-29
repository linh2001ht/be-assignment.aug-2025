from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Date, Enum
from datetime import date
from typing import List, Optional
from . import Base
from .enums import TaskStatus, Priority

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO, index=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.LOW, index=True)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignee: Mapped["User"] = relationship(back_populates="assigned_tasks")
    comments: Mapped[List["Comment"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    attachments: Mapped[List["Attachment"]] = relationship(back_populates="task", cascade="all, delete-orphan")
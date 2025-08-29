from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from . import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped["Task"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from . import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(String(500))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
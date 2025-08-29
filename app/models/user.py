from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from passlib.hash import bcrypt
from typing import List
from .enums import Role
from . import Base
from .user_project import user_project

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[Role] = mapped_column(default=Role.MEMBER)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    organization: Mapped["Organization"] = relationship(back_populates="users")
    projects: Mapped[List["Project"]] = relationship(secondary=user_project, back_populates="users", passive_deletes=True)
    assigned_tasks: Mapped[List["Task"]] = relationship(back_populates="assignee")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")

    def set_password(self, password: str):
        self.hashed_password = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)
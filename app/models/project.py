from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from app.database import Base
from .user_project import user_project

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    organization: Mapped["Organization"] = relationship(back_populates="projects")
    users: Mapped[list["User"]] = relationship(secondary=user_project, back_populates="projects", passive_deletes=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
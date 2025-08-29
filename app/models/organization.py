from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List
from . import Base

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    users: Mapped[List["User"]] = relationship(back_populates="organization")
    projects: Mapped[List["Project"]] = relationship(back_populates="organization")
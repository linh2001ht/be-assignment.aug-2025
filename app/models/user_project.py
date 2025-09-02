from sqlalchemy import Table, Column, ForeignKey
from app.database import Base

user_project = Table(
    "user_project",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)

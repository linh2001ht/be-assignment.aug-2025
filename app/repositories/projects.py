from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import Project, User
from typing import Any

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def create_with_member(self, creator: User, **kwargs: Any) -> Project:
        project = self.model(**kwargs)
        project.users.append(creator)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    

    def get_by_organization(self, organization_id: int) -> list[Project]:
        return self.db.query(self.model).filter(self.model.organization_id == organization_id).all()

    def add_user(self, project: Project, user: User) -> User:
        if user not in project.users:
            project.users.append(user)
            self.db.commit()
            self.db.refresh(project)
        return user

    def remove_user(self, project: Project, user: User) -> None:
        if user in project.users:
            project.users.remove(user)
            self.db.commit()
            self.db.refresh(project)

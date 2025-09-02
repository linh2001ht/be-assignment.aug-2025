from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import Organization

class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: Session):
        super().__init__(db, Organization)

    def get_by_name(self, name: str) -> Organization | None:
        return self.db.query(self.model).filter(self.model.name == name).first()
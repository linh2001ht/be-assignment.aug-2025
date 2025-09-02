from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(self.model).filter(self.model.email == email).first()
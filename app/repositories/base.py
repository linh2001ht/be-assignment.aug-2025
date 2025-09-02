from typing import Generic, TypeVar, Type, Any, List
from sqlalchemy.orm import Session
from app.database import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: Any) -> T | None:
        return self.db.query(self.model).get(id)

    def create(self, **kwargs: Any) -> T:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: T, **kwargs: Any) -> T:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.commit()
        
    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()
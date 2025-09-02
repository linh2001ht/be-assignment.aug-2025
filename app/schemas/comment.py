from datetime import datetime
from pydantic import BaseModel

class CommentBase(BaseModel):
    content: str

class CommentRead(CommentBase):
    id: int
    user_id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True
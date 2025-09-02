from datetime import datetime
from pydantic import BaseModel

class AttachmentBase(BaseModel):
    filename: str
    path: str
    size: int

class AttachmentRead(AttachmentBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True
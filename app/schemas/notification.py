from datetime import datetime
from pydantic import BaseModel

class NotificationBase(BaseModel):
    message: str
    is_read: bool = False

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationRead(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

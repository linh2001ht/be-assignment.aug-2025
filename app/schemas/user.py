from pydantic import BaseModel, EmailStr
from app.models import Role

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str    

class UserUpdate(UserBase):
    role: Role | None = None
    organization_id: int | None = None

class UserAddOrg(BaseModel):
    user_id: int
    role: Role = Role.MEMBER

class UserRead(UserBase):
    id: int
    role: Role
    organization_id: int | None = None

    class Config:
        from_attributes = True
